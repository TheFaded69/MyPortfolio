"""Геометрия.
"""
import math
import operator
import vtk


class Plane(vtk.vtkPlane):
    def __init__(self, origin=(0, 0, 0), normal=(1, 0, 0)):
        super().__init__()
        self.origin = origin
        self.normal = normal

    @property
    def origin(self):
        return self.GetOrigin()

    @origin.setter
    def origin(self, value):
        self.SetOrigin(*value)

    @property
    def normal(self):
        return self.GetNormal()

    @normal.setter
    def normal(self, value):
        self.SetNormal(*value)

    # нормаль xz =(1,0,0); XY =(0,0,1), YZ =(0,1,0)
    @classmethod
    def XY(cls, origin=(0, 0, 0)):
        return cls(normal=(0, 0, 1), origin=origin)

    @classmethod
    def XZ(cls, origin=(0, 0, 0)):
        return cls(normal=(1, 0, 0), origin=origin)

    @classmethod
    def YZ(cls, origin=(0, 0, 0)):
        return cls(normal=(0, 1, 0), origin=origin)


def vec_add(x, y):
    """Суммирование векторов.

    :param x: входной вектор
    :param y: входной вектор
    :return: сумма векторов
    """
    return tuple(map(operator.add, x, y))


def vec_subtract(x, y):
    """Разность векторов.

    :param x: входной вектор
    :param y: входной вектор

    :return разность векторов
    """
    return tuple(map(operator.sub, x, y))


def vec_dot(x, y):
    """Скалярное произведение векторов.

    :param x: входной вектор
    :param y: входной вектор
    :return скалярное произведение векторов
    """
    return sum(map(operator.mul, x, y))


def vec_norm(x):
    """Норма вектора.

    :param x: входной вектор
    :return норму вектора (скаляр)
    """
    return math.sqrt(vec_dot(x, x))


def vec_normalize(x):
    """Нормализация вектора.

    :param x: входной вектор
    :return нормализованный вектор
    """
    x_norm = vec_norm(x)
    return tuple(c / x_norm for c in x)


def vec_angle(x, y):
    """Угол между векторами.

    :param x: входной вектор
    :param y: входной вектор
    :return угол между векторами в радианах
    """
    return math.acos(vec_dot(x, y) / (vec_norm(x) * vec_norm(y)))


def vec_cross(x, y):
    """Векторное произведение векторов.

    :param x: входной вектор
    :param y: входной вектор
    :return вектор - результат векторного произведения.
    """
    return [x[1] * y[2] - x[2] * y[1],
            x[2] * y[0] - x[0] * y[2],
            x[0] * y[1] - x[1] * y[0]]


def vec_project(x, y):
    """Вычисление проекции вектора `x` на вектор `y`.

    :param x: входной вектор
    :param y: входной вектор
    :return проекцию
    """
    vector2norm = vec_normalize(y)
    vector1component = vec_dot(x, vector2norm)
    return [vector1component * vector2norm[0],
            vector1component * vector2norm[1],
            vector1component * vector2norm[2]]


def vec_tangent(x, normal):
    """Тангенциальный компонент вектора для заданной нормали.

    :param x: вектор.
    :param normal: нормаль
    :return тангенциальный компонент
    """
    s = vec_dot(x, normal)
    return tuple(xc - s * nc for xc, nc in zip(x, normal))


def point_distance(x, y):
    """Эвклидово расстояние между точками.

    :param x: первая точка
    :param y: вторая точка
    :return число с плавающей точкой - эвклидово расстояние между точками.
    """
    return math.sqrt(sum(map(lambda a, b: pow(a - b, 2), x, y)))


def rad2deg(radians: float) -> float:
    """Преобразование радиан в градусы.

    :param radians: угол в радианах
    :return угол в градусах
    """
    return 180.0 * radians / math.pi


def deg2rad(degrees: float) -> float:
    """Преобразование градусов в радианы

    :param degrees: угол в градусах
    :return угол в градусах
    """
    return math.pi * degrees / 180.0


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


def fit_implant(implant, bone, nx=5, ny=5, nz=1):
    # Для каждого бокса
    result = implant.copy()
    boxes = implant.subboxes(nx=nx, ny=ny, nz=nz)

    for box in boxes:
        pt_idxs = implant.points_in_box(box)
        # Только непустые
        if len(pt_idxs) > 0:
            # Найти точку для которой наименьшее расстояние
            vec = None
            min_dist = 100000.0
            for pt in implant.points[pt_idxs]:
                closest_pt_id = bone.find_closest_point(pt)
                closest_pt_coords = bone.points[closest_pt_id, :]
                distance = point_distance(pt, closest_pt_coords)
                if distance < min_dist:
                    min_dist = distance
                    vec = pt - closest_pt_coords
            result.points[pt_idxs] -= vec
    result.Modified()
    return result
