import heapq
import math
from collections import namedtuple
from operator import attrgetter
from numbers import Number

import numpy as np
import vtk
from libcore.mixins import InplaceMix, inplaceble
from vtk.util.numpy_support import numpy_to_vtk
from vtk.util.numpy_support import numpy_to_vtkIdTypeArray
from vtk.util.numpy_support import vtk_to_numpy

from .geometry import transform, point_distance

__all__ = ['Mesh']


class Mesh(vtk.vtkPolyData, InplaceMix):

    def __init__(self, *args, **kwargs):
        super().__init__()

        # Если параметров нет - создаем пустой меш
        if not args:
            return
        elif (len(args) == 1) and isinstance(args[0], vtk.vtkPolyData):
            self.DeepCopy(args[0])
        elif (len(args) == 1) and isinstance(args[0], str):
            self.load(args[0])
        else:
            raise TypeError('Неправильный тип аргументов')

        self._roi = None
        self._locator = None

    def load(self, file_name):
        """ Загрузка меша из файла.

        Подерживаеются ASCII и binary ply и stl

        Параметры
        ---------
        filename : str
            Имя файла с мешем для загрузки. Тип файла определяется по расширению файла.

        Примечания
        ----------
        Бинарные файлы загружаются значительно быстрее чем ASCII.

        """

        # Выбор необходимого ридера на основе расширения файла
        if file_name.lower().endswith('ply'):
            # Тип PLY
            reader = vtk.vtkPLYReader()
        elif file_name.lower().endswith('stl'):
            # Тип STL
            reader = vtk.vtkSTLReader()
        else:
            raise Exception('Поддерживаются только файлы типа "ply" и "stl"')

        # Загрузка файла
        from libcore.utils import link_to_file
        reader.SetFileName(link_to_file(file_name))
        # reader.SetFileName(file_name)
        reader.Update()
        self.DeepCopy(reader.GetOutput())

    def save(self, file_name, binary=True):
        """ Запись меша на диск.

        Запись возможна в бинарные или ASCII файлы форматов ply, stl


        Параметры
        ---------
        file_name : str
            Имя файла для записи меша. Тип файла определяется по расширению файла.
            Может быть одним из:
                - .ply
                - .stl

        Замечания
        ---------
        Запись бинарных файлов осуществляется много быстрее чем ASCII-файлов.
        """

        # Проверка типов файлов
        if file_name.lower().endswith('stl'):
            writer = vtk.vtkSTLWriter()
        elif file_name.lower().endswith('ply'):
            writer = vtk.vtkPLYWriter()
        else:
            raise Exception('Поддерживаются типы файлов "ply", "stl"')

        # Осуществляем запись
        from libcore.utils import link_to_file
        writer.SetFileName(link_to_file(file_name))
        if binary:
            writer.SetFileTypeToBinary()
        else:
            writer.SetFileTypeToASCII()
        writer.SetInputData(self)
        writer.Write()

    @property
    def roi(self):
        if self._roi is None:
            return np.ones((self.number_of_points,), dtype=np.bool)
        else:
            return self._roi

    @roi.setter
    def roi(self, roi_mask):
        if not isinstance(roi_mask, np.ndarray):
            raise TypeError('Точки должны быть представленны в виде массива numpy')
        self._roi = roi_mask

    @property
    def points(self):
        points_ = None
        if self.GetPoints():
            points_ = vtk_to_numpy(self.GetPoints().GetData())
        return points_

    @property
    def normals(self):
        normals_ = None
        if self.GetPointData().GetNormals():
            normals_ = vtk_to_numpy(self.GetPointData().GetNormals())
        return normals_

    @points.setter
    def points(self, points_array):
        if not isinstance(points_array, np.ndarray):
            raise TypeError('Точки должны быть представленны в виде массива numpy')

        # Проверка. Данные должны быть расположенны непрерывно
        if not points_array.flags['C_CONTIGUOUS']:
            points_array = np.ascontiguousarray(points_array)

        vtk_points = vtk.vtkPoints()
        vtk_points.SetData(numpy_to_vtk(points_array, deep=True))
        self.SetPoints(vtk_points)

    @property
    def faces(self):
        return vtk_to_numpy(self.GetPolys().GetData()).reshape((-1, 4))

    @faces.setter
    def faces(self, value):
        if value.ndim != 2:
            raise Exception('Faces should be a 2D array')
        elif value.shape[1] != 4:
            raise Exception(
                'First column should contain the number of points per face')

        vtkcells = vtk.vtkCellArray()
        vtkcells.SetCells(value.shape[0], numpy_to_vtkIdTypeArray(value, deep=True))
        self.SetPolys(vtkcells)

    @property
    def number_of_points(self):
        return len(self.points)

    @property
    def number_of_faces(self):
        return len(self.faces)

    @property
    def number_of_cells(self):
        return self.GetNumberOfCells()

    # @property
    # def center(self):
    #     """ Центр масс меша """
    #     com = vtk.vtkCenterOfMass()
    #     com.SetInputData(self)
    #     com.Update()
    #     center_estimate = com.GetCenter()
    #     valid = True
    #     for val in center_estimate:
    #         if not isinstance(val, Number):
    #             valid = False
    #
    #     print('Mesh.center computation is performed, result is: {}'.format(center_estimate))
    #     if valid:
    #         return center_estimate
    #     else:
    #         return 0.0, 0.0, 0.0

    @property
    def center(self):
        x0, x1, y0, y1, z0, z1 = self.bounds
        cx = float(x0 + abs(x1-x0)/2)
        cy = float(y0 + abs(y1-y0)/2)
        cz = float(z0 + abs(z1 - z0)/2)
        return cx, cy, cz

    @property
    def bounds(self):
        # bbox
        self.ComputeBounds()
        return self.GetBounds()

    @property
    def min_x(self):
        return self.bounds[0]

    @property
    def max_x(self):
        return self.bounds[1]

    @property
    def min_y(self):
        return self.bounds[2]

    @property
    def max_y(self):
        return self.bounds[3]

    @property
    def min_z(self):
        return self.bounds[4]

    @property
    def max_z(self):
        return self.bounds[5]

    @property
    def volume(self):
        """ Объем ограничиваемый мешем """
        volume_ = 0
        cmp = vtk.vtkMassProperties()
        cmp.SetInputData(self)
        cmp.Update()
        volume_ = cmp.GetVolume()
        return volume_

    @property
    def area(self):
        """ """
        properties = vtk.vtkMassProperties()
        properties.SetInput(self)
        properties.Update()
        return properties.GetSurfaceArea()

    @property
    def num_points(self):
        """ Количество точек в меше"""
        num_points_ = 0
        if self.is_initialized:
            num_points_ = len(self.points)

        return num_points_

    @property
    def num_cells(self):
        """ Количество ячеек в меше """
        return self.GetNumberOfCells()

    @property
    def num_regions(self):
        """ Количество связных областей в меше"""
        # TODO: всю работу со связными областями оформить отдельно
        connectivity_filter = vtk.vtkPolyDataConnectivityFilter()
        connectivity_filter.SetInputData(self)
        connectivity_filter.SetExtractionModeToAllRegions()
        connectivity_filter.Update()
        num_regions = connectivity_filter.GetNumberOfExtractedRegions()
        return num_regions

    @property
    def outline(self):
        outline_filter = vtk.vtkOutlineFilter()
        outline_filter.SetInputData(self)
        outline_filter.Update()
        return Mesh(outline_filter.GetOutput())

    @property
    def number_of_open_edges(self):
        edges = vtk.vtkFeatureEdges()
        edges.FeatureEdgesOff()
        edges.BoundaryEdgesOn()
        edges.NonManifoldEdgesOn()
        edges.SetInputData(self)
        edges.Update()
        return edges.GetOutput().GetNumberOfCells()

    @property
    def is_closed(self):
        return self.number_of_open_edges == 0

    @property
    def number_of_non_manifold_edges(self):
        edges = vtk.vtkFeatureEdges()
        edges.FeatureEdgesOff()
        edges.BoundaryEdgesOff()
        edges.NonManifoldEdgesOn()
        edges.SetInputData(self)
        edges.Update()

        return edges.GetOutput().GetNumberOfCells()

    @property
    def is_manifold(self):
        return self.number_of_non_manifold_edges == 0

    @property
    def number_of_regions(self):
        pdcf = vtk.vtkPolyDataConnectivityFilter()
        pdcf.SetInputData(self)
        pdcf.SetExtractionModeToAllRegions()
        pdcf.Update()
        return pdcf.GetNumberOfExtractedRegions()

    def copy(self):
        """ Создание полностью независимой новой копии данных"""
        polydata = vtk.vtkPolyData()
        polydata.DeepCopy(self)
        return Mesh(polydata)

    @inplaceble
    def scale(self, sx, sy, sz):
        """ Масштабирование меша по каждой из осей"""
        return transform(self, ttype='scale', sx=sx, sy=sy, sz=sz)

    @inplaceble
    def move(self, dx=0, dy=0, dz=0):
        """ Перемещение меша """
        return transform(self, ttype='move', dx=dx, dy=dy, dz=dz)

    @inplaceble
    def rotate_x(self, angle):
        """     """
        return transform(self, ttype='rotate', rx=angle)

    @inplaceble
    def rotate_y(self, angle):
        """     """
        return transform(self, ttype='rotate', ry=angle)

    @inplaceble
    def rotate_z(self, angle):
        return transform(self, ttype='rotate', rz=angle)

    @inplaceble
    def apply_transform(self, T):
        return transform(self, ttype='transform', T=T)

    @inplaceble
    def reflect(self, plane='x'):
        return transform(self, ttype='reflect', plane=plane)

    @inplaceble
    def triangular(self):
        """ Возвращает меш только из треугольников.

        Более сложные полигоны будут разбиты на треугольники (это всегда можно сделать).

        Возвращает
        ----------
        mesh_prop : Mesh
            Меш, ячейками которого являются только треугольники.
        """
        triangular_filter = vtk.vtkTriangleFilter()
        triangular_filter.SetInputData(self)
        triangular_filter.PassVertsOff()
        triangular_filter.PassLinesOff()
        triangular_filter.Update()

        return triangular_filter.GetOutput()

    @inplaceble
    def reverse_sense(self):
        reverse = vtk.vtkReverseSense()
        reverse.SetInputData(self)
        reverse.ReverseCellsOn()
        reverse.ReverseNormalsOn()
        reverse.Update()
        return reverse.GetOutput()

    @inplaceble
    def strip(self):
        stripper = vtk.vtkStripper()
        stripper.SetInputData(self)
        stripper.Update()
        return Mesh(stripper.GetOutput())

    @inplaceble
    def reconstruct_surface(self):
        surf = vtk.vtkSurfaceReconstructionFilter()
        surf.SetInputData(self)

        contourFilter = vtk.vtkContourFilter()
        contourFilter.SetInputConnection(surf.GetOutputPort())
        contourFilter.SetValue(0, 0.0)

        # Sometimes the contouring algorithm can create a volume whose gradient
        # vector and ordering of polygon (using the right hand rule) are
        # inconsistent. vtkReverseSense cures this problem.
        reverse = vtk.vtkReverseSense()
        reverse.SetInputConnection(contourFilter.GetOutputPort())
        reverse.ReverseCellsOn()
        reverse.ReverseNormalsOn()
        reverse.Update()
        return reverse.GetOutput()

    @inplaceble
    def clean(self):
        """ Удаление точек-дубликатов, неиспользуемых точек, вырожденных ячеек

        Параметры
        ---------

        """
        clean = vtk.vtkCleanPolyData()
        #clean.SetTolerance(0.01)
        clean.SetInputData(self)
        clean.Update()

        return clean.GetOutput()

    @inplaceble
    def decimate(self, algorithm='quadric', preserve_topology=True, reduction=0.5):
        """ Децимация меша """
        if algorithm == 'quadric':
            decimator = vtk.vtkQuadricDecimation()
        elif algorithm == 'pro':
            decimator = vtk.vtkDecimatePro()
            decimator.SetPreserveTopology(preserve_topology)
        else:
            decimator = vtk.vtkQuadricClustering()

        if hasattr(decimator, 'SetTargetReduction'):
            decimator.SetTargetReduction(reduction)

        decimator.SetInputData(self)
        decimator.Update()
        mesh = decimator.GetOutput()
        return mesh

    @inplaceble
    def close_mesh(mesh):
        triang = vtk.vtkContourTriangulator()
        triang.SetInputData(mesh.open_edges)
        triang.Update()
        contours = Mesh(triang.GetOutput())
        filled = Mesh.from_meshes([mesh, contours])
        filled.clean(inplace=True)
        return filled

    @inplaceble
    def smooth(self, iterations=20):
        """ Сглаживание меша """
        pass_band = 0.001
        feature_angle = 120.0
        iterations = 20

        smoother = vtk.vtkWindowedSincPolyDataFilter()
        smoother.SetInputData(self)
        smoother.SetNumberOfIterations(iterations)
        smoother.BoundarySmoothingOff()
        smoother.FeatureEdgeSmoothingOff()
        smoother.SetFeatureAngle(feature_angle)
        smoother.SetPassBand(pass_band)
        smoother.NonManifoldSmoothingOn()
        smoother.NormalizeCoordinatesOn()
        smoother.Update()

        return smoother.GetOutput()

    @inplaceble
    def remove_small_objects(self, ratio=0.5):
        """ """
        max_size, _ = next(self.split(self, n_largest=1))
        result = Mesh()
        for size, mesh in self.split(self, return_size=True):
            if size > max_size * ratio:
                result += mesh
        return result

    @inplaceble
    def fill_holes(self, hole_size=1000):
        fill_holes = vtk.vtkFillHolesFilter()
        fill_holes.SetInputData(self)
        fill_holes.SetHoleSize(hole_size)
        fill_holes.Update()

        return fill_holes.GetOutput()

    @inplaceble
    def subdivide(self, levels=2, algorithm='linear'):
        algorithm = algorithm.lower()
        if algorithm == 'linear':
            sfilter = vtk.vtkLinearSubdivisionFilter()
        elif algorithm == 'butterfly':
            sfilter = vtk.vtkButterflySubdivisionFilter()
        else:
            sfilter = vtk.vtkLoopSubdivisionFilter()

        sfilter.SetNumberOfSubdivisions(levels)
        sfilter.SetInputData(self)
        sfilter.Update()
        return sfilter.GetOutput()

    def compute_original_ids(self):
        array = self.GetPointData().GetArray("OriginalIds")
        if array:
            return self
        else:
            id_filter = vtk.vtkIdFilter()
            id_filter.SetInputData(self)
            id_filter.PointIdsOn()
            id_filter.SetIdsArrayName("OriginalIds")
            id_filter.Update()

            surface_filter = vtk.vtkDataSetSurfaceFilter()
            surface_filter.SetInputConnection(id_filter.GetOutputPort())
            surface_filter.Update()
            return Mesh(surface_filter.GetOutput())

    def get_original_ids(self):
        result = []
        idx_array = self.GetPointData().GetArray("OriginalIds")
        if idx_array:
            for i in range(idx_array.GetNumberOfValues()):
                result.append(idx_array.GetValue(i))
        return result

    def get_original_ids_cells(self):
        result = []
        idx_array = self.GetCellData().GetArray("OriginalIds")
        if idx_array:
            for i in range(idx_array.GetNumberOfValues()):
                result.append(idx_array.GetValue(i))
        return result


    def filter_visible(self, renderer):
        visible_selector = vtk.vtkSelectVisiblePoints()
        visible_selector.SetInputData(self)
        visible_selector.SetRenderer(renderer)
        visible_selector.Update()
        return Mesh(visible_selector.GetOutput())

    def select_frustum(self, frustum):
        extract_poly_data_geometry = vtk.vtkExtractPolyDataGeometry()
        extract_poly_data_geometry.SetInputData(self)
        extract_poly_data_geometry.SetImplicitFunction(frustum)
        extract_poly_data_geometry.Update()
        return Mesh(extract_poly_data_geometry.GetOutput())

    def select_sphere(self, center, radius):
        sphere = vtk.vtkSphere()
        sphere.SetCenter(center)
        sphere.SetRadius(radius)
        extract_poly_data_geometry = vtk.vtkExtractPolyDataGeometry()
        extract_poly_data_geometry.SetInputData(self)
        extract_poly_data_geometry.SetImplicitFunction(sphere)
        extract_poly_data_geometry.Update()
        return Mesh(extract_poly_data_geometry.GetOutput())

    def slice_by_plane(self, plane):
        cutter = vtk.vtkCutter()
        cutter.SetInputData(self)
        cutter.SetCutFunction(plane)
        cutter.GenerateValues(1, 0.0, 0.0)
        stripper = vtk.vtkStripper()
        stripper.SetInputConnection(cutter.GetOutputPort())
        stripper.Update()
        return Mesh(stripper.GetOutput())

    def slice_by_mesh(self, mesh):
        cut_by_impl = vtk.vtkImplicitPolyDataDistance()
        cut_by_impl.SetInput(mesh)

        cutter = vtk.vtkCutter()
        cutter.SetCutFunction(cut_by_impl)
        cutter.SetInputData(self)

        surface_filter = vtk.vtkDataSetSurfaceFilter()
        surface_filter.SetInputConnection(cutter.GetOutputPort())
        surface_filter.Update()

        return Mesh(surface_filter.GetOutput())

    def disect_by_plane(self, plane):
        clipper = vtk.vtkClipPolyData()
        clipper.SetInputData(self)
        clipper.SetClipFunction(plane)
        clipper.SetGenerateClippedOutput(1)
        clipper.Update()
        #clipper.GetClippedOutput()

        return [Mesh(clipper.GetOutput()),
                Mesh(clipper.GetClippedOutput())]

    @inplaceble
    def clip_by_mesh(self, mesh, inverse=False):
        """ Выделить часть меша, ограниченную другим мешем
        """
        if isinstance(mesh, vtk.vtkPlanes):
            es = vtk.vtkExtractPolyDataGeometry()
            es.SetInputData(self)
            es.SetImplicitFunction(mesh)
            es.SetExtractInside(not inverse)
            es.Update()
            return Mesh(es.GetOutput())
        else:
            # Используем трехмерную триангуляцию делоне, чтобы разбить меш на примитивы
            # Наверное можно без этого
            tri = vtk.vtkDelaunay3D()
            tri.SetInputData(mesh)
            tri.BoundingTriangulationOff()

            # Нужна какая-нибудь скалярная величина, чтобы понимать где нутрь, а где наружа
            elev = vtk.vtkElevationFilter()
            elev.SetInputConnection(tri.GetOutputPort())
            elev.Update()

            # Преобразуем в неявную функию
            implicit = vtk.vtkImplicitDataSet()
            implicit.SetDataSet(elev.GetOutput())

            # Оставляем только ту часть меша what (предположительно более сложного)
            # Которая находится внутри меша by_what
            cpd = vtk.vtkClipPolyData()
            cpd.SetClipFunction(implicit)
            cpd.SetInputData(self)
            cpd.SetInsideOut(inverse)
            cpd.Update()
            return Mesh(cpd.GetOutput())

    @inplaceble
    def clip_by_mesh2(self, mesh, inverse=False):
        # Преобразуем в неявную функию
        implicit = vtk.vtkImplicitDataSet()
        implicit.SetDataSet(mesh)

        # Оставляем только ту часть меша what (предположительно более сложного)
        # Которая находится внутри меша by_what
        cpd = vtk.vtkClipPolyData()
        cpd.SetClipFunction(implicit)
        cpd.SetInputData(self)
        cpd.SetInsideOut(inverse)
        cpd.Update()
        return Mesh(cpd.GetOutput())

    @inplaceble
    def clip_by_mesh3(self, mesh, inverse=False):
        # Преобразуем в неявную функию
        implicit = vtk.vtkImplicitPolyDataDistance()
        implicit.SetInput(mesh)

        # Оставляем только ту часть меша what (предположительно более сложного)
        # Которая находится внутри меша by_what
        cpd = vtk.vtkClipPolyData()
        cpd.SetClipFunction(implicit)
        cpd.SetInputData(self)
        cpd.SetInsideOut(inverse)
        cpd.Update()
        return Mesh(cpd.GetOutput())


    @inplaceble
    def extract_largest(self):
        """Extract largest of several disconnected regions."""
        connect = vtk.vtkPolyDataConnectivityFilter()
        connect.SetInputData(self)
        connect.SetExtractionModeToLargestRegion()
        connect.Update()
        return Mesh(connect.GetOutput())

    def split(self, n_largest=0, n_smallest=0, return_size=False):
        """ Разделение меша на связные компоненты """
        data_type = type(self)
        pdcf = vtk.vtkPolyDataConnectivityFilter()
        pdcf.SetInputData(self)
        pdcf.SetExtractionModeToAllRegions()
        pdcf.Update()

        region = namedtuple('region', ['SIZE', 'index'])
        num_regions = pdcf.GetNumberOfExtractedRegions()
        indexes = list(range(num_regions))
        sizes = vtk_to_numpy(pdcf.GetRegionSizes()).tolist()
        regions = [region(SIZE=size, index=index) for size, index in zip(sizes, indexes)]

        if n_largest > 0:
            regions = heapq.nlargest(n_largest, regions, key=attrgetter('SIZE'))
        elif n_smallest > 0:
            regions = heapq.nsmallest(n_smallest, regions, key=attrgetter('SIZE'))

        pdcf.SetExtractionModeToSpecifiedRegions()
        for size, idx in regions:
            pdcf.AddSpecifiedRegion(idx)
            pdcf.Update()
            if return_size:
                yield size, data_type(pdcf.GetOutput())
            else:
                yield data_type(pdcf.GetOutput())
            pdcf.DeleteSpecifiedRegion(idx)

    def split2(self):
        pdcf = vtk.vtkPolyDataConnectivityFilter()
        pdcf.SetInputData(self)
        pdcf.SetExtractionModeToAllRegions()
        pdcf.Update()

    def extract_closest_region(self, point=(0.0, 0.0, 0.0)):
        connectivity_filter = vtk.vtkPolyDataConnectivityFilter()
        connectivity_filter.SetInputData(self)
        connectivity_filter.SetExtractionModeToClosestPointRegion()
        connectivity_filter.SetClosestPoint(point)
        connectivity_filter.Update()
        return Mesh(connectivity_filter.GetOutput())

    def find_closest_point(self, point=(0.0, 0.0, 0.0)):
        if not self._locator:
            self._locator = vtk.vtkPointLocator()
            self._locator.SetDataSet(self)
            self._locator.BuildLocator()

        return self._locator.FindClosestPoint(point)

    @inplaceble
    def vector_extrude(self, direction=(1.0, 0.0, 0.0)):
        nx, ny, nz = direction
        extruder = vtk.vtkLinearExtrusionFilter()
        extruder.SetInputData(self)
        extruder.SetExtrusionTypeToVectorExtrusion()
        extruder.SetVector(-nx, -ny, -nz)
        #extruder.SetCapping(True)
        extruder.Update()
        return Mesh(extruder.GetOutput())

    def is_inside(self, point=(0, 0, 0)):
        marker = vtk.vtkSelectEnclosedPoints()
        marker.SetTolerance(1e-4)
        marker.Initialize(self)
        answer = marker.IsInsideSurface(*point)
        marker.Complete()
        return answer

    def points_in_box(self, box):
        marker = vtk.vtkSelectEnclosedPoints()
        marker.SetTolerance(0.1)
        marker.Initialize(box)

        idxs = []
        for idx, point in enumerate(self.points):
            if marker.IsInsideSurface(point):
                idxs.append(idx)

        marker.Complete()
        return idxs

    def subboxes(self, nx=10, ny=10, nz=1, oversize=''):
        """
        Передавать результат mesh.outline для разбиения оутлайна на взаимонепересекающиеся меши
        :param outline:
        :param nx:
        :param ny:
        :param nz:
        :return:
        """
        points = self.outline.points

        origin = points[0]  # Угол, выбранный за отсчет координат
        dir_x = points[1] - points[0]  # Вектор в направлении оси иксов
        dir_y = points[2] - points[0]  # Вектор в направлении оси игреков
        dir_z = points[4] - points[0]  # Вектор в направлении оси z

        if oversize == 'x':
            origin = origin - dir_x
            dir_x *= 2
        if oversize == 'y':
            origin = origin - dir_y
            dir_y *= 2
        if oversize == 'z':
            origin = origin - dir_z
            dir_z *= 2

        wx = 1.0 / nx  # Ширина блока по x
        wy = 1.0 / ny  # Ширина блока по y
        wz = 1.0 / nz  # Ширина блока по z
        boxes = []
        for cx in range(nx):
            for cy in range(ny):
                for cz in range(nz):
                    x = wx * cx
                    y = wy * cy
                    z = wz * cz

                    x = [origin + x * dir_x + y * dir_y + z * dir_z,
                         origin + (x + wx) * dir_x + y * dir_y + z * dir_z,
                         origin + x * dir_x + (y + wy) * dir_y + z * dir_z,
                         origin + x * dir_x + y * dir_y + (z + wz) * dir_z,
                         origin + (x + wx) * dir_x + (y + wy) * dir_y + z * dir_z,
                         origin + x * dir_x + (y + wy) * dir_y + (z + wz) * dir_z,
                         origin + (x + wx) * dir_x + y * dir_y + (z + wz) * dir_z,
                         origin + (x + wx) * dir_x + (y + wy) * dir_y + (z + wz) * dir_z]

                    pts = [(0, 1, 4, 2),
                           (4, 7, 5, 2),
                           (5, 7, 6, 3),
                           (3, 6, 1, 0),
                           (0, 2, 5, 3),
                           (1, 4, 7, 6)]

                    cube = vtk.vtkPolyData()
                    points = vtk.vtkPoints()
                    polys = vtk.vtkCellArray()

                    for i, xi in enumerate(x):
                        points.InsertPoint(i, xi)
                    for pt in pts:
                        polys.InsertNextCell(mkVtkIdList(pt))

                    cube.SetPoints(points)
                    cube.SetPolys(polys)

                    boxes.append(Mesh(cube))

        return boxes

    @inplaceble
    def resample(self, nx=40, ny=40, nz=40, value=0.0):
        implicit = vtk.vtkImplicitPolyDataDistance()
        implicit.SetInput(self)

        sample = vtk.vtkSampleFunction()
        sample.SetImplicitFunction(implicit)
        sample.SetModelBounds(*self.bounds)
        sample.SetSampleDimensions(nx, ny, nz)
        sample.CappingOff()

        surface = vtk.vtkContourFilter()
        surface.SetInputConnection(sample.GetOutputPort())
        surface.SetValue(0, value)
        surface.ComputeNormalsOn()
        surface.ComputeGradientsOn()
        surface.Update()

        return surface.GetOutput()

    @inplaceble
    def boolean_intersection(self, mesh, loopy=True):
        if loopy:
            boolean_filter = vtk.vtkLoopBooleanPolyDataFilter()
        else:
            boolean_filter = vtk.vtkBooleanOperationPolyDataFilter()
        boolean_filter.SetOperationToIntersection()
        boolean_filter.SetInputData(0, self)
        boolean_filter.SetInputData(1, mesh)
        #boolean_filter.ReorientDifferenceCellsOn()
        boolean_filter.Update()
        mesh = boolean_filter.GetOutput()
        return mesh

    @inplaceble
    def boolean_difference(self, mesh, loopy=True):
        if loopy:
            boolean_filter = vtk.vtkLoopBooleanPolyDataFilter()
        else:
            boolean_filter = vtk.vtkBooleanOperationPolyDataFilter()
        boolean_filter = vtk.vtkBooleanOperationPolyDataFilter()
        boolean_filter.SetOperationToDifference()
        boolean_filter.SetInputData(0, self)
        boolean_filter.SetInputData(1, mesh)
        boolean_filter.ReorientDifferenceCellsOn()
        boolean_filter.Update()
        mesh = boolean_filter.GetOutput()
        return mesh

    @inplaceble
    def boolean_union(self, mesh, loopy=True):
        if loopy:
            boolean_filter = vtk.vtkLoopBooleanPolyDataFilter()
        else:
            boolean_filter = vtk.vtkBooleanOperationPolyDataFilter()

        boolean_filter = vtk.vtkBooleanOperationPolyDataFilter()
        boolean_filter.SetOperationToUnion()
        boolean_filter.SetInputData(0, self)
        boolean_filter.SetInputData(1, mesh)
        boolean_filter.ReorientDifferenceCellsOn()
        boolean_filter.Update()
        mesh = boolean_filter.GetOutput()
        return mesh

    @classmethod
    def line(cls, point1, point2):
        """Отрезок прямой между точками.

        :param point1: точка на прямой
        :param point2: точка на прямой
        :return Полигональный меш
        """
        source = vtk.vtkLineSource()
        source.SetPoint1(point1)
        source.SetPoint2(point2)
        source.Update()
        return cls(source.GetOutput())

    @classmethod
    def plane(cls, plane, resolution_x=10,
              resolution_y=10):
        """Плоскость.

        :param point1:
        :param point2:
        :param origin:
        :param normal:

        :return полигональный меш

        """
        source = vtk.vtkPlaneSource()
        source.SetOrigin(plane.origin)
        source.SetNormal(plane.normal)
        source.SetXResolution(resolution_x)
        source.SetYResolution(resolution_y)
        source.Update()
        return cls(source.GetOutput())

    @classmethod
    def sphere(cls, center=(0.0, 0.0, 0.0), radius=2.0, resolution_theta=31, resolution_phi=31):
        """Сфера.

        :param center: центр сферы
        :param radius: радиус
        :param resolution_theta: разрешение вдоль параметра theta
        :param resolution_phi: разрешение вдоль параметра phi
        :return: полигональный меш
        """
        source = vtk.vtkSphereSource()
        source.SetCenter(center)
        source.SetRadius(radius)
        source.SetThetaResolution(resolution_theta)
        source.SetPhiResolution(resolution_phi)
        source.Update()

        mesh = cls(source.GetOutput())
        mesh.triangular(inplace=True)
        return mesh

    @classmethod
    def arrow(cls, tip_length=1.0, tip_radius=0.5, shaft_radius=0.2, tip_resolution=31, shaft_resolution=21,
              tesselation_level=3):
        """Стрелка

        :return:
        """
        source = vtk.vtkArrowSource()
        source.SetTipResolution(tip_resolution)
        source.SetShaftResolution(shaft_resolution)
        source.SetShaftRadius(shaft_radius)
        source.SetTipRadius(tip_radius)
        source.SetTipLength(tip_length)
        source.Update()
        mesh = cls(source.GetOutput())
        mesh.triangular(inplace=True)
        mesh.subdivide(levels=tesselation_level, inplace=True)
        return mesh

    @classmethod
    def torus(cls, crossection_radius=0.5, ring_radius=1.0, resolution_u=51, resolution_v=51, resolution_w=51):
        """Тор

        :return:
        """
        parametric_tours = vtk.vtkParametricTorus()
        parametric_tours.SetCrossSectionRadius(crossection_radius)
        parametric_tours.SetRingRadius(ring_radius)
        source = vtk.vtkParametricFunctionSource()
        source.SetParametricFunction(parametric_tours)
        source.SetUResolution(resolution_u)
        source.SetVResolution(resolution_v)
        source.SetWResolution(resolution_w)
        source.Update()
        mesh = cls(source.GetOutput())
        mesh.reconstruct_surface(inplace=True)
        return mesh

    def reflect_around_plane(self, plane):
        for idx in range(self.number_of_points):
            pt = self.points[idx, :].astype(np.float32)
            pxyz = [0, 0, 0]
            vtk.vtkPlane.ProjectPoint(list(pt), plane.GetOrigin(), plane.GetNormal(), pxyz)
            projection = np.array(pxyz, dtype=np.float32)
            self.points[idx, :] = projection
        self.Modified()

    @classmethod
    def cube(cls, width=2.0, height=2.0, depth=2.0, tesselation_level=2):
        """

        :param bounds:
        :return:
        """
        source = vtk.vtkTessellatedBoxSource()
        source.SetLevel(tesselation_level)
        source.QuadsOn()
        source.SetBounds(-0.5 * width, 0.5 * width, -0.5 * height, 0.5 * height, -0.5 * depth, 0.5 * depth)
        source.Update()
        mesh = cls(source.GetOutput())
        mesh.triangular(inplace=True)
        mesh.subdivide(levels=tesselation_level, inplace=True)
        return mesh

    @classmethod
    def cone(cls, radius=1.0, resolution=21, height=1.0, tesselation_level=2):
        """Конус.

        """
        source = vtk.vtkConeSource()
        source.SetResolution(resolution)
        source.SetHeight(height)
        source.SetRadius(radius)
        source.Update()
        mesh = cls(source.GetOutput())
        mesh.triangular(inplace=True)
        mesh.subdivide(levels=tesselation_level, algorithm='linear', inplace=True)
        return mesh

    @classmethod
    def cylinder(cls, center=(0.0, 0.0, 0.0), radius=1.0, height=1.0, resolution=31, capping=True, tesselation_level=2):
        """Цилиндр.
        """
        source = vtk.vtkCylinderSource()
        source.SetCapping(capping)
        source.SetResolution(resolution)
        source.SetRadius(radius)
        source.SetCenter(center)
        source.SetHeight(height)
        source.Update()
        mesh = cls(source.GetOutput())
        mesh.triangular(inplace=True)
        mesh.subdivide(levels=tesselation_level, inplace=True)
        mesh.clean(inplace=True)
        return mesh

    @classmethod
    def tetrahedra(cls, tesselation_level=2):
        """Тетраэдр.
        """
        source = vtk.vtkPlatonicSolidSource()
        source.SetSolidTypeToTetrahedron()
        source.Update()
        mesh = cls(source.GetOutput())
        mesh.triangular(inplace=True)
        mesh.subdivide(levels=tesselation_level, inplace=True)
        return mesh

    @classmethod
    def octahedron(cls, tesselation_level=2):
        """Октаэдр.
        """
        source = vtk.vtkPlatonicSolidSource()
        source.SetSolidTypeToOctahedron()
        source.Update()
        mesh = cls(source.GetOutput())
        mesh.triangular(inplace=True)
        mesh.subdivide(levels=tesselation_level, inplace=True)
        return mesh

    @classmethod
    def icosahedron(cls, tesselation_level=2):
        """Икосаэдр.
        """
        source = vtk.vtkPlatonicSolidSource()
        source.SetSolidTypeToIcosahedron()
        source.Update()
        mesh = cls(source.GetOutput())
        mesh.triangular(inplace=True)
        mesh.subdivide(levels=tesselation_level, inplace=True)
        return mesh

    @classmethod
    def dodecahedron(cls, tesselation_level=2):
        """Додекаэдр.
        """
        source = vtk.vtkPlatonicSolidSource()
        source.SetSolidTypeToDodecahedron()
        source.Update()
        mesh = cls(source.GetOutput())
        mesh.triangular(inplace=True)
        mesh.subdivide(levels=tesselation_level, inplace=True)
        return mesh

    @classmethod
    def box(cls, bounds, level=5):
        source = vtk.vtkTessellatedBoxSource()
        source.SetBounds(bounds)
        source.SetLevel(5)
        source.Update()
        mesh = cls(source.GetOutput())
        return mesh

    @classmethod
    def from_meshes(cls, meshes_list):
        """ Соединение данных несколькоих полигональных мешей в один"""
        appender = vtk.vtkAppendPolyData()
        for mesh in meshes_list:
            appender.AddInputData(mesh)
        appender.Update()
        return cls(appender.GetOutput())

    @classmethod
    def from_points(cls, points_list):
        poly_data = vtk.vtkPolyData()
        pts_ = vtk.vtkPoints()
        for x, y, z in points_list:
            pts_.InsertNextPoint((x, y, z))
        lines = vtk.vtkCellArray()
        lines.InsertNextCell(len(points_list)+1)
        for i in range(len(points_list)):
            lines.InsertCellPoint(i)
        lines.InsertCellPoint(0)
        poly_data.SetPoints(pts_)
        poly_data.SetLines(lines)
        return cls(poly_data)

    @inplaceble
    def warp(self, vecs):
        warp_data = vtk.vtkDoubleArray()
        warp_data.SetNumberOfComponents(3)
        warp_data.SetName("warpData")

        for vec in vecs:
            warp_data.InsertNextTuple(list(vec))

        self.GetPointData().AddArray(warp_data)
        self.GetPointData().SetActiveVectors(warp_data.GetName())

        warp_vector = vtk.vtkWarpVector()
        warp_vector.SetInputData(self)
        warp_vector.Update()
        return Mesh(warp_vector.GetOutput())

    def overwrite(self, data):
        """ Перезаписывает старые данные меша новыми

        Параметры
        ---------
        mesh_prop : vtk.vtkPolyData или Mesh
            Меш, данными которого перезаписываемThe overwriting mesh_prop.

        """
        self._locator = None
        self.SetPoints(data.GetPoints())
        self.SetPolys(data.GetPolys())
        self.BuildCells()
        self.Modified()

    def __str__(self):
        info = ''
        info += 'Number of points: {}\n'.format(self.number_of_points)
        info += 'Number of faces: {}\n'.format(self.number_of_faces)
        info += 'Number of cells: {}\n'.format(self.number_of_cells)
        info += 'Number of regions: {}\n'.format(self.number_of_regions)
        info += 'Closed: {}\n'.format(self.is_closed)
        info += 'Manifold: {}\n'.format(self.is_manifold)
        info += 'Number of border edges: {}\n'.format(self.number_of_open_edges)
        info += 'Number of non-manifold edges: {}\n'.format(self.number_of_non_manifold_edges)
        return info

    @property
    def open_edges(self):
        edge_extractor = vtk.vtkFeatureEdges()
        edge_extractor.SetInputData(self)
        edge_extractor.BoundaryEdgesOn()
        edge_extractor.FeatureEdgesOff()
        edge_extractor.Update()
        return Mesh(edge_extractor.GetOutput())

    def compute_normals(self):
        comp_norm = vtk.vtkPolyDataNormals()
        comp_norm.SetInputData(self)
        comp_norm.Update()
        self.ShallowCopy(comp_norm.GetOutput())

    @inplaceble
    def mask_on_ratio(self, ratio=2):
        masker = vtk.vtkMaskPolyData()
        masker.SetInputData(self)
        masker.SetOnRatio(ratio)
        masker.Update()
        return masker.GetOutput()

def show(objectdicts, label=''):
    # Initialize render window
    ren = vtk.vtkRenderer()
    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(ren)
    iren = vtk.vtkRenderWindowInteractor()
    style = vtk.vtkInteractorStyleTrackballActor()
    iren.SetInteractorStyle(style)
    iren.SetRenderWindow(renWin)

    # Add each actor
    for objectdict in objectdicts:

        # If dict item exists use specified value, otherwise use default value
        polydata = objectdict.get('polydata')  # default is None
        color = objectdict.get('get_color', [1, 1, 1])
        opacity = objectdict.get('opacity', 1)

        if not polydata:  # only add actor if polydata is specified
            continue

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(polydata)
        mapper.ScalarVisibilityOff()
        actor = vtk.vtkActor()
        actor.GetProperty().SetColor(color)
        actor.GetProperty().SetOpacity(opacity)
        actor.SetMapper(mapper)
        ren.AddActor(actor)

    # Add text actor
    if label:
        txt = vtk.vtkTextActor()
        txt.SetInput(label)
        txtprop = txt.GetTextProperty()
        txtprop.SetFontFamilyToArial()
        txtprop.SetFontSize(18)
        txtprop.SetColor(0, 0, 0)
        txt.SetDisplayPosition(20, 30)
        ren.AddActor(txt)

    # Renderer (window) specifications
    ren.SetBackground(82 / 255., 87 / 255., 110 / 255.)  # Paraview default
    renWin.SetSize(640, 480)
    ren.ResetCamera()
    ren.GetActiveCamera().Zoom(1)

    # Start rendering
    iren.Initialize()
    renWin.Render()
    iren.Start()


def transform(mesh, ttype, **kwargs):
    """
        transfomation:
            - transform
            - scale
            - move
            - rotate
            - reflect
    """
    data_type = type(mesh)
    if ttype in ('scale', 'move', 'rotate', 'transform'):
        if ttype == 'scale':
            # Масштабирование меша по каждой из осей
            sx = kwargs.get('sx', 1.0)
            sy = kwargs.get('sy', 1.0)
            sz = kwargs.get('sz', 1.0)
            T = vtk.vtkTransform()
            T.Identity()
            T.Scale(sx, sy, sz)

        elif ttype == 'move':
            # Перемещение меша
            dx = kwargs.get('dx', 0.0)
            dy = kwargs.get('dy', 0.0)
            dz = kwargs.get('dz', 0.0)
            T = vtk.vtkTransform()
            T.Identity()
            T.Translate(dx, dy, dz)

        elif ttype == 'rotate':
            """     """
            rx = kwargs.get('rx', 0.0)
            ry = kwargs.get('ry', 0.0)
            rz = kwargs.get('rz', 0.0)
            T = vtk.vtkTransform()
            T.Identity()
            T.RotateX(rx)
            T.RotateY(ry)
            T.RotateZ(rz)

        elif ttype == 'transform':
            T = kwargs['T']
        T.Modified()

        tpdf = vtk.vtkTransformPolyDataFilter()
        tpdf.SetInputData(mesh)
        tpdf.SetTransform(T)
        tpdf.Update()
        result = tpdf.GetOutput()


    elif ttype == 'reflect':
        plane_mapping = {'x': vtk.vtkReflectionFilter.USE_X,
                         'y': vtk.vtkReflectionFilter.USE_Y,
                         'z': vtk.vtkReflectionFilter.USE_Z,
                         'x_max': vtk.vtkReflectionFilter.USE_X_MAX,
                         'y_max': vtk.vtkReflectionFilter.USE_Y_MAX,
                         'z_max': vtk.vtkReflectionFilter.USE_Z_MAX,
                         'x_min': vtk.vtkReflectionFilter.USE_X_MIN,
                         'y_min': vtk.vtkReflectionFilter.USE_Y_MIN,
                         'z_min': vtk.vtkReflectionFilter.USE_Z_MIN}
        plane = plane_mapping[kwargs.get('plane', 'x')]

        rf = vtk.vtkReflectionFilter()
        rf.SetInputData(mesh)
        rf.CopyInputOff()
        rf.SetPlane(plane)

        sf = vtk.vtkDataSetSurfaceFilter()
        sf.SetInputConnection(rf.GetOutputPort())
        sf.Update()
        result = sf.GetOutput()

    return data_type(result)


def extact(mesh, extractable, inverse=False):
    """ Можно извлечь:
        - vtkSelection - ячейки, точки и т.д.
        - Некоторую часть меша, огриниченную плоскостями
        Меш на основе некоторого ограничения
    """
    data_type = type(mesh)
    if isinstance(extractable, vtk.vtkSelection):
        if inverse:
            node = extractable.GetNode(0)
            node.GetProperties().Set(vtk.vtkSelectionNode.INVERSE(), 1)
        es = vtk.vtkExtractSelection()
        es.SetInputData(0, mesh)
        es.SetInputData(1, extractable)
        gf = vtk.vtkGeometryFilter()
        gf.SetInputConnection(es.GetOutputPort())
        gf.Update()
        result = gf.GetOutput()

    elif isinstance(extractable, vtk.vtkPolyData):
        # Используем трехмерную триангуляцию делоне, чтобы разбить меш на примитивы
        # Наверное можно без этого
        tri = vtk.vtkDelaunay3D()
        tri.SetInputData(mesh)
        tri.BoundingTriangulationOff()

        # Нужна какая-нибудь скалярная величина, чтобы понимать где нутрь, а где наружа
        elev = vtk.vtkElevationFilter()
        elev.SetInputConnection(tri.GetOutputPort())
        elev.Update()

        # Преобразуем в неявную функию
        implicit = vtk.vtkImplicitDataSet()
        implicit.SetDataSet(elev.GetOutput())

        # Оставляем только ту часть меша what (предположительно более сложного)
        # Которая находится внутри меша by_what
        cpd = vtk.vtkClipPolyData()
        cpd.SetClipFunction(implicit)
        cpd.SetInputData(mesh)
        cpd.SetInsideOut(inverse)
        cpd.Update()

        result = cpd.GetOutput()

    elif isinstance(extractable, (vtk.vtkPlanes, vtk.vtkSphere)):
        es = vtk.vtkExtractPolyDataGeometry()
        es.SetInputData(mesh)
        es.SetImplicitFunction(extractable)
        es.SetExtractInside(not inverse)
        es.Update()
        result = es.GetOutput()

    return data_type(result)


def save_mesh_to_hdf(fd, name, mesh):
    grp = fd.create_group(name)
    grp['points'] = mesh.points
    grp['faces'] = mesh.faces
    fd.flush()


def read_mesh_from_hdf(fd, name):
    mesh = Mesh()
    group = fd[name]
    mesh.points = group['points'].value
    mesh.faces = group['faces'].value
    return mesh

def limiter(value):
    if value > 0.0:
        return value
    else:
        return 0.0

def square_warp(mesh, indexes, center, direction, length):
    warp_vectors = [list([0.0, 0.0, 0.0]) for idx in range(mesh.number_of_points)]
    for idx in indexes:
        point = mesh.points[idx]
        dist = point_distance(center, point)
        warp_vectors[idx] = [limiter(length-dist) * n for n in direction]

    mesh.warp(vecs=warp_vectors, inplace=True)


def mkVtkIdList(it):
    """
    Makes a vtkIdList from a Python iterable. I'm kinda surprised that
     this is necessary, since I assumed that this kind of thing would
     have been built into the wrapper and happen transparently, but it
     seems not.

    :param it: A python iterable.
    :return: A vtkIdList
    """
    vil = vtk.vtkIdList()
    for i in it:
        vil.InsertNextId(int(i))
    return vil
