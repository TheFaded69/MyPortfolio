import math
import vtk

from libcore.mixins import ViewportMixin
from libcore.mesh import Mesh
from libcore.display import PolyActor


def make_circle():
    pd = vtk.vtkPolyData()
    points = vtk.vtkPoints()

    num_pts = 21
    for i in range(0, num_pts):
        angle = 2.0 * math.pi * i / 20.0
        points.InsertPoint(i, 0.1 * math.cos(angle),
                           0.1 * math.sin(angle), 0.0)
        # lines.InsertNextCell(i)
    vertex_indices = list(range(0, num_pts))
    vertex_indices.append(0)
    lines = vtk.vtkCellArray()
    lines.InsertNextCell(num_pts + 1, vertex_indices)

    pd.SetPoints(points)
    pd.SetLines(lines)
    return pd

def gen_random_pc(num_points=100, radius=20.0):
    """Генерация случайного облака точек"""
    # Генерируем облако случайных точек
    point_source = vtk.vtkPointSource()
    point_source.SetNumberOfPoints(num_points)
    point_source.SetRadius(radius)
    point_source.Update()
    cloud = Mesh()
    cloud.ShallowCopy(point_source.GetOutput())
    return cloud

def delaunay_surface(mesh):
    """C помощью этой функции можно находить ограничивающую поверхность для облака точек"""
    points = vtk.vtkPoints()
    points.DeepCopy(mesh.GetPoints())
    profile = vtk.vtkPolyData()
    profile.SetPoints(points)
    delny = vtk.vtkDelaunay3D()
    delny.SetInputData(profile)
    delny.SetTolerance(0.001)
    delny.Update()
    surface = vtk.vtkDataSetSurfaceFilter()
    surface.SetInputData(delny.GetOutput())
    surface.Update()
    return Mesh(surface.GetOutput())


def polydata_to_ugrid(mesh):
    """Преобразование данных меша в неструктурированную сетку"""
    points = vtk.vtkPoints()
    points.DeepCopy(mesh.GetPoints())
    profile = vtk.vtkPolyData()
    profile.SetPoints(points)
    delny = vtk.vtkDelaunay3D()
    delny.SetInputData(profile)
    delny.SetTolerance(0.001)
    delny.Update()
    ugrid = delny.GetOutput()
    return ugrid


def ugrid_to_polydata(ugrid):
    """Преобразование данных на неструктурированной сетке в полигональный меш"""
    surface = vtk.vtkDataSetSurfaceFilter()
    surface.SetInputData(ugrid)
    surface.Update()
    mesh = Mesh(surface.GetOutput())
    return mesh


def append_ugrids(ugrids):
    return ugrids[0]


def make_polyline(points):
    pts = vtk.vtkPoints()
    for pt in points:
        pts.InsertNextPoint(pt)

    polyline = vtk.vtkPolyLine()
    polyline.GetPointIds().SetNumberOfIds(len(points))
    for i in range(0, len(points)):
        polyline.GetPointIds().SetId(i, i)

    cells = vtk.vtkCellArray()
    cells.InsertNextCell(polyline)
    polydata = vtk.vtkPolyData()
    polydata.SetPoints(pts)
    polydata.SetLines(cells)
    return Mesh(polydata)

def make_tube(polyline, radius=1.0, number_of_sides=50):
    tube_filter = vtk.vtkTubeFilter()
    tube_filter.SetInputData(polyline)
    tube_filter.SetRadius(radius)
    tube_filter.SetNumberOfSides(number_of_sides)
    tube_filter.Update()
    result = Mesh(tube_filter.GetOutput())
    return result

class App(ViewportMixin):

    def __init__(self):
        super().__init__()
        points = [[-1.0, -1.0, -1.0],
                  [0.0, 0.0, 0.0],
                  [1.0, 0.0, 0.0],
                  [2.0, 0.0, 0.0],
                  [2.5, 0.5, 0.0],
                  [2.8, 0.6, 1.0],
                  [2.8, 0.6, 2.0]]

        self.random_mesh = delaunay_surface(gen_random_pc(num_points=200, radius=1.0))
        self.random_actor = PolyActor(mesh=self.random_mesh, color='blue', opacity=0.2)

        self.contour_polyline = make_polyline(points=points)
        self.contour_actor = PolyActor(mesh=self.contour_polyline, color='red', line_width=2.0)

        self.tube_mesh = make_tube(self.contour_polyline, radius=0.5)
        self.tube_actor = PolyActor(mesh=self.tube_mesh, color='yellow', opacity=0.2)

        self.add_props([self.random_actor,
                        self.contour_actor,
                        self.tube_actor])


        self.contour_representation = vtk.vtkOrientedGlyphContourRepresentation()
        self.contour_representation.GetLinesProperty().SetColor(1.0, 0.0, 0.0)

        self.contour_widget = vtk.vtkContourWidget()
        self.contour_widget.SetInteractor(self.interactor)
        self.contour_widget.SetRepresentation(self.contour_representation)
        self.contour_widget.On()



        self.pd = make_circle()
        self.contour_widget.Initialize(self.pd, 1)
        self.contour_widget.Render()



if __name__ == '__main__':
    app = App()
    app.run()