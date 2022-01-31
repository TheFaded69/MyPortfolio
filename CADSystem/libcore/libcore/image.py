""" Средства для работы с волюметрическими изображениями

**Image** -- Класс, содержащий данные изображения и инкапсулирующий методы работы с ним

- load_file: загрузка файла
-
"""
import numpy as np
import vtk
from libcore.mixins import InplaceMix, inplaceble
from vtk.util.numpy_support import get_vtk_array_type
from vtk.util.numpy_support import numpy_to_vtk
from vtk.util.numpy_support import vtk_to_numpy
from .mesh import Mesh

__all__ = ['Image']


class Image(vtk.vtkImageData, InplaceMix):
    """ """

    def __init__(self, *args, **kwargs):
        super().__init__()

        self._modality = 'ct'

        # Если параметров нет - пустое изображение
        if not args:
            return
        elif (len(args) == 1) and isinstance(args[0], vtk.vtkImageData):
            self.DeepCopy(args[0])
        elif (len(args) == 1) and isinstance(args[0], str):
            self.load(args[0])
        else:
            raise TypeError('Неправильный тип аргументов')

    @property
    def modality(self):
        return self._modality

    @modality.setter
    def modality(self, val):
        if val.lower() in ['ct', 'mr', 'mri']:
            self._modality = val.lower()
            if self._modality == 'mr':
                self._modality = 'mri'

    def is_ct(self):
        return self.modality == 'ct'

    def is_mri(self):
        return self.modality == 'mri'

    @property
    def is_initialized(self):
        return not self.GetPointData() is None

    @property
    def width(self):
        dimensions = self.GetDimensions()
        return dimensions[0]

    @property
    def height(self):
        dimensions = self.GetDimensions()
        return dimensions[1]

    @property
    def depth(self):
        dimensions = self.GetDimensions()
        return dimensions[2]

    @property
    def bounds(self):
        """ Ограничивающий прямоугольник изображения """
        return self.GetBounds()

    @property
    def center(self):
        x0, x1, y0, y1, z0, z1 = self.bounds
        width = abs(x1 - x0)
        height = abs(y1 - y0)
        depth = abs(z1 - z0)
        cx = x0 + width / 2
        cy = y0 + height / 2
        cz = z0 + depth / 2
        return (cx, cy, cz)

    @property
    def spacings(self):
        """ Расстояния между вокселями по осям """
        return self.GetSpacing()

    @property
    def min_value(self):
        """Минимальное значение плотности после нормировки"""
        return self.GetScalarRange()[0]

    @property
    def max_value(self):
        """Максимальное значение плотности после нормировки"""
        return self.GetScalarRange()[1]

    @property
    def voxels(self):
        return vtk_to_numpy(self.GetPointData().GetScalars()).reshape(self.height, self.width, self.depth)

    def load(self, file_name):
        if file_name.lower().endswith('.vti'):
            reader = vtk.vtkXMLImageDataReader()
        else:
            raise Exception('Поддерживаются только "vti" файлы')

        from libcore.utils import link_to_file
        reader.SetFileName(link_to_file(file_name))
        reader.Update()
        self.DeepCopy(reader.GetOutput())

    def save(self, file_name):
        if file_name.lower().endswith('.vti'):
            writer = vtk.vtkXMLImageDataWriter()
        else:
            raise Exception('Поддерживаются только "vti" файлы')
        writer.SetInputData(self)
        from libcore.utils import link_to_file
        writer.SetFileName(link_to_file(file_name))
        writer.Write()

    @inplaceble
    def shift_scale(self, scale=1.0, shift=0.0):
        shift_scale = vtk.vtkImageShiftScale()
        shift_scale.SetScale(scale)
        shift_scale.SetShift(shift)
        shift_scale.SetInputData(self)
        shift_scale.Update()
        return shift_scale.GetOutput()

    @inplaceble
    def clip_values(self, minimum_value=-2048, maximum_value=2048):
        thresh = vtk.vtkImageThreshold()
        thresh.SetInputData(self)
        thresh.ThresholdByLower(minimum_value)
        thresh.ReplaceInOn()
        thresh.SetInValue(minimum_value)
        thresh.ThresholdByUpper(maximum_value)
        thresh.ReplaceInOn()
        thresh.SetInValue(maximum_value)
        thresh.Update()

        return thresh.GetOutput()

    @inplaceble
    def denoise(self, factor=1.0, threshold=10.0):
        """
        Подавление шума послойно на скане

        anisotropic_diffusion2d - использует итеративный алгоритм анизотропной
        диффузии для подавления шумовой компоненты на двумерных изображениях.

        :param image: входное двумерное или трехмерное изображение (vtkImageData)
        :param factor: определяет степень влияния соседей на оценку значения пикселя
        :param threshold: пороговое значение градиента для учета соседа в диффузии
        :return: обработанное изображение (vtkImageData)

        В случае, когда входное изображение является трехмерным - обработка будет
        производится послойно. Будут использоваться только соседи внутри двумерного
        среза.

        """
        denoise = vtk.vtkImageAnisotropicDiffusion2D()
        denoise.SetInputData(self)
        denoise.SetDiffusionFactor(factor)
        denoise.SetDiffusionThreshold(threshold)
        denoise.Update()

        return denoise.GetOutput()

    @inplaceble
    def median3d(self, kernel_size=(3, 3, 3)):
        """
        median3d - медианная фильтрация трехмерного изображения

        :param image: входное изображение (vtkImageData)
        :param SIZE: размер локальной области для выбора медианного значения
        :return: результат фильтрации (vtkImageData)

        Медианный фильтр заменяет значение каждого пикселя на медианное значение из прямоугольной области
        окружающей его.

        """
        median = vtk.vtkImageMedian3D()
        median.SetInputData(self)
        median.SetKernelSize(kernel_size[0], kernel_size[1], kernel_size[2])
        median.Update()

        return median.GetOutput()

    @inplaceble
    def enhance(self):
        """
        sharp - увеличивает резкость изображения в соответствии с фактором factor

        :param image: Входной объект vtkImageData
        :param factor: коэффициент увеличения резкости
        :return:
        """
        # Обработку будем выполнять в формате double
        cast = vtk.vtkImageCast()
        cast.SetInputData(self)
        cast.SetOutputScalarTypeToDouble()
        cast.Update()

        # Считаем лаплассиан
        laplacian = vtk.vtkImageLaplacian()
        laplacian.SetInputData(cast.GetOutput())
        laplacian.SetDimensionality(3)
        laplacian.Update()

        # Вычитаем лаплассиан из изображения
        enhance = vtk.vtkImageMathematics()
        enhance.SetInputData(0, cast.GetOutput())
        enhance.SetInputData(1, laplacian.GetOutput())
        enhance.SetOperationToSubtract()
        enhance.Update()

        return enhance.GetOutput()

    @inplaceble
    def flip(self, axis='x'):
        plane_mapping = {'x': 0,
                         'y': 1,
                         'z': 2}
        plane = plane_mapping[axis]

        rf = vtk.vtkImageFlip()
        rf.SetFilteredAxis(plane)
        rf.SetInputData(self)
        rf.Update()
        return rf.GetOutput()


    @inplaceble
    def smooth(self, sigma=4.0, window=2.0):
        """
        gaussian_smooth реализует свертку входного изображения с гауссовым ядром.
        Поддерживает размерности ядра 2 и 3.

        :param image: входное изображение (vtkImageData)
        :param r: радиус ядра
        :param sigma: величина стандартного отклонения ядра гауссиана
        :return: сглаженное изображение (vtkImageData)

        """
        smooth = vtk.vtkImageGaussianSmooth()
        smooth.SetInputData(self)
        smooth.SetDimensionality(3)
        smooth.SetRadiusFactor(window)
        smooth.SetStandardDeviation(sigma)
        smooth.Update()
        return smooth.GetOutput()

    def extract_contour(self, isovalue=400):
        iso = vtk.vtkContourFilter()
        iso.SetInputData(self)
        iso.SetValue(0, isovalue)
        iso.Update()
        return Mesh(iso.GetOutput())

    def extract_surface(self, threshold=400, threshold2=None, discrete=True, largest_only=False) -> Mesh:
        """ Извлечение поверхности соответствующей значениям в диапазоне """
        if discrete:
            thresholder = vtk.vtkImageThreshold()
            thresholder.SetInputData(self)

            if threshold2:
                # Если задано два порога - берем только между ними
                thresholder.ThresholdBetween(threshold, threshold2)
            else:
                thresholder.ThresholdByLower(threshold)

            thresholder.ReplaceInOn()
            thresholder.SetInValue(0)
            thresholder.ReplaceOutOn()
            thresholder.SetOutValue(1)

            extractor = vtk.vtkDiscreteMarchingCubes()
            extractor.ComputeGradientsOff()
            extractor.ComputeNormalsOff()
            extractor.ComputeScalarsOff()
            extractor.SetInputConnection(thresholder.GetOutputPort())
            extractor.GenerateValues(1, 1, 1)
        else:
            extractor = vtk.vtkMarchingCubes()
            extractor.ComputeGradientsOff()
            extractor.ComputeNormalsOff()
            extractor.ComputeScalarsOff()
            extractor.SetInputData(self)
            extractor.SetValue(0, threshold)

        extractor.Update()
        mesh = Mesh(extractor.GetOutput())
        mesh.reverse_sense(inplace=True)  # Исправляем неправлиные грани (порядок обхода не тот и т.д.)
        if largest_only:
            # Извлечь только самую большую поверхность (может не работать если есть железо в кадре)
            mesh.extract_largest(inplace=True)

        return mesh

    def extract_surface2(self, threshold=400):
        mesh = None
        return mesh


    def overwrite(self, data):
        """ Перезаписывает старые данные меша новыми

        Параметры
        ---------
        mesh_prop : vtk.vtkPolyData или Mesh
            Меш, данными которого перезаписываемThe overwriting mesh_prop.

        """
        print('inplace')
        self.ShallowCopy(data)

    def __str__(self):
        repr = 'width = {}\n'.format(self.width)
        repr += 'height = {}\n'.format(self.height)
        repr += 'depth = {}'.format(self.depth)
        repr += 'min_value = {}'.format(self.min_value)
        repr += 'max_value = {}'.format(self.max_value)
        return repr

    def as_numpy(self):
        array = vtk_to_numpy(self.GetPointData().GetScalars())
        width, height, depth = self.GetDimensions()
        if depth == 1:
            return array.reshape((height, width, 3))
        else:
            array = array.reshape((depth, height, width))
            return np.swapaxes(array, 0, 2)

    def save_to_hdf(self, fd, name):
        grp = fd.create_group(name)
        grp['image'] = self.as_numpy()
        grp['spacings'] = np.array(self.spacings)
        grp['origin'] = np.array(self.GetOrigin())
        fd.flush()

    @classmethod
    def from_hdf(cls, fd, name):
        grp = fd[name]
        arr = grp['image'].value

        print(arr.shape)
        image = cls.from_numpy(array=arr,
                                 spacing=grp['spacings'].value,
                                 origin=grp['origin'].value)
        return image

    @classmethod
    def from_numpy(cls, array, spacing=(1.0, 1.0, 1.0), origin=(0.0, 0.0, 0.0), modality='ct'):
        depth, height, width = array.shape
        dimensions = [width, height, depth]
        array_type = get_vtk_array_type(array.dtype)

        image = cls()
        image.modality = modality
        image_array = numpy_to_vtk(array.ravel(),
                                   deep=True,
                                   array_type=array_type)
        image.SetDimensions(dimensions)
        image.SetSpacing(spacing)
        image.SetOrigin(origin)
        image.GetPointData().SetScalars(image_array)
        return image

# def load_image(directory='../../../taz/DICOM', uid='6007'):
#     metadata = dicom.scan_directory()
#     sorted = dict()
#     for key, val in metadata.items():
#         if val['series_instance_uid'].endswith('6007'):
#             sorted[key] = val
#     sorted = dicom.sort_files(list(sorted.keys()))
#     image = dicom.read_volume(sorted)
#     return image
