# Сделать полосу с правильными нормалями?
# 1. (+) Линию интерполировать
# 2. (+) Выбирать точки примерно через <константа>
# TODO: 3. Отделить точки, которые близко к мешу черепа
# TODO: 4. Сделать ленту в виде <Implicit>
# TODO: 5. Вычесть из ленты цилиндры

# Построение пластинки
import numpy as np
import vtk
import math

from libcore.mixins import ViewportMixin
from libcore.display import PolyActor
from libcore.mesh import Mesh
from libcore.geometry import vec_add
from libcore.geometry import point_distance


def get_normal(mesh, point):
    pt_idx = mesh.find_closest_point(point)
    normal = mesh.normals[pt_idx]
    return [-x for x in normal]


def mega_tube(pt1, pt2, radius=0.8):
    source = vtk.vtkLineSource()
    source.SetPoint1(pt1)
    source.SetPoint2(pt2)
    source.Update()

    tube_filter = vtk.vtkTubeFilter()
    tube_filter.SetInputData(source.GetOutput())
    tube_filter.SetCapping(True)
    tube_filter.SetRadius(radius)
    tube_filter.SetNumberOfSides(24)
    tube_filter.Update()
    return Mesh(tube_filter.GetOutput())


def make_ribbon(polyline, width=2.0):
    """Делает из линии ленту нулевой толщины и заданной ширины"""
    ribbon_filter = vtk.vtkRibbonFilter()
    ribbon_filter.SetInputData(polyline)
    ribbon_filter.SetWidth(width)
    ribbon_filter.Update()
    result = Mesh(ribbon_filter.GetOutput())
    return result

def normal_extrude(mesh, length=1.0):
    mesh.compute_normals()
    extruder = vtk.vtkLinearExtrusionFilter()
    extruder.SetInputData(mesh)
    extruder.SetExtrusionTypeToNormalExtrusion()
    extruder.SetCapping(True)
    extruder.SetScaleFactor(length)
    extruder.Update()
    return Mesh(extruder.GetOutput())

def implicitize(mesh, value=0.01):
    """Запускать при окончательной подготовке импланта"""
    implicit = vtk.vtkImplicitPolyDataDistance()
    implicit.SetInput(mesh)

    sample = vtk.vtkSampleFunction()
    sample.SetImplicitFunction(implicit)
    sample.SetModelBounds(*mesh.bounds)
    sample.SetSampleDimensions(120, 120, 120)
    sample.CappingOff()

    surface = vtk.vtkContourFilter()
    surface.SetInputConnection(sample.GetOutputPort())
    surface.SetValue(0, value)
    surface.ComputeNormalsOn()
    surface.ComputeGradientsOn()
    surface.Update()

    return Mesh(surface.GetOutput())


def to_implicit(mesh):
    imp = vtk.vtkImplicitPolyDataDistance()
    imp.SetInput(mesh)
    return imp

def implicitly_combine(main, to_add_list, to_subtract_list):
    all_meshes = [main]
    all_meshes.extend(to_add_list)
    all_meshes.extend(to_subtract_list)
    all_mesh = Mesh.from_meshes(all_meshes)
    bounding_box = all_mesh.bounds
    del all_mesh


    main_imp = to_implicit(main)
    to_add_imp = [to_implicit(mesh) for mesh in to_add_list]
    to_subtract_imp = [to_implicit(mesh) for mesh in to_subtract_list]

    boolean_sum = vtk.vtkImplicitBoolean()
    boolean_sum.SetOperationTypeToUnion()
    boolean_sum.AddFunction(main_imp)
    for mesh in to_add_imp:
        boolean_sum.AddFunction(mesh)

    boolean_diff = vtk.vtkImplicitBoolean()
    boolean_diff.SetOperationTypeToDifference()
    boolean_diff.AddFunction(boolean_sum)
    for mesh in to_subtract_imp:
        boolean_diff.AddFunction(mesh)

    sampler = vtk.vtkSampleFunction()
    sampler.SetImplicitFunction(boolean_diff)
    sampler.SetModelBounds(bounding_box)
    sampler.SetSampleDimensions(120, 120, 120)

    surface = vtk.vtkContourFilter()
    surface.SetInputConnection(sampler.GetOutputPort())
    surface.SetValue(0, 0.001)
    surface.Update()

    return Mesh(surface.GetOutput())

def interpolate_polyline(polyline, subdivisions=256):
    spline = vtk.vtkSplineFilter()
    spline.SetInputData(polyline)
    spline.SetSubdivideToSpecified()
    spline.SetNumberOfSubdivisions(256)
    spline.Update()
    return Mesh(spline.GetOutput())

class SurfaceProbe(object):

    def __init__(self, interactor, mesh, actor):
        self.interactor = interactor
        self.mesh = mesh

        self.point_placer = vtk.vtkPolygonalSurfacePointPlacer()
        self.point_placer.GetPolys().AddItem(mesh)
        self.point_placer.AddProp(actor)
        self.point_placer.SnapToClosestPointOn()

        self.widget = vtk.vtkContourWidget()
        self.widget.SetInteractor(interactor)
        self.widget.SetPriority(1.0)

        self.representation = self.widget.GetRepresentation()
        self.representation.AlwaysOnTopOn()
        self.representation.SetLineInterpolator(vtk.vtkLinearContourLineInterpolator())
        self.representation.GetLinesProperty().RenderPointsAsSpheresOn()
        self.representation.SetPointPlacer(self.point_placer)

    @property
    def points(self):
        return Mesh(self.representation.GetContourRepresentationAsPolyData())

    def show(self):
        self.widget.On()

    def hide(self):
        self.widget.Off()


def choose_closest(polyline, mesh, maximum_distance=1.0):
    good_points = []
    for pt in polyline.points:
        closest_idx = mesh.find_closest_point(pt)
        closest_point = mesh.points[closest_idx]
        distance = point_distance(pt, closest_point)
        if distance < maximum_distance:
            good_points.append(pt)
    return Mesh.from_points(good_points)

def thin_out(polyline, minimum_step=10.0):
    good_points = []
    first_point, last_point = polyline.points[1], polyline.points[-1]
    good_points.append(first_point)
    current_point = first_point
    for pt in polyline.points:
        distance = point_distance(current_point, pt)
        if distance >= minimum_step:
            good_points.append(pt)
            current_point = pt
    good_points.append(last_point)
    return Mesh.from_points(good_points)

class App(ViewportMixin):

    def __init__(self):
        super().__init__()
        self.tube = None
        self.polyline = None
        self.skull_mesh = Mesh('stage8/pet_1.stl')
        self.implant_mesh = Mesh('stage8/pet_2.stl')
        self.full_mesh = Mesh.from_meshes([self.skull_mesh,
                                           self.implant_mesh])

        self.actor = PolyActor(mesh=self.full_mesh, color='red')
        self.add_prop(self.actor)

        self.curve_widget = SurfaceProbe(interactor=self.interactor,
                                  mesh=self.full_mesh,
                                  actor=self.actor)
        self.curve_widget.show()
        self.register_callback(vtk.vtkCommand.CharEvent, self.on_char)

    def on_char(self, caller, event):
        key = self.interactor.GetKeySym()
        if key == '1':
            self.full_mesh.compute_normals()
            print('Number of points before: {}'.format(len(self.curve_widget.points.points)))
            polyline = interpolate_polyline(self.curve_widget.points, subdivisions=256)
            print('Number of points after: {}'.format(len(polyline.points)))
            # normals = [self.full_mesh.normals[self.full_mesh.find_closest_point(pt)] for pt in polyline.points]
            # polyline.normals = normals
            polyline = choose_closest(polyline, self.skull_mesh, maximum_distance=1.0)
            print('Number of points after choose closest: {}'.format(len(polyline.points)))

            polyline = thin_out(polyline, minimum_step=10.0)
            print('Number of points after thin out: {}'.format(len(polyline.points)))


            tube = make_ribbon(polyline, width=3.0)
            tube = normal_extrude(tube, length=10.0)
            self.myactor = PolyActor(mesh=tube, color='blue', opacity=0.3)
            self.add_prop(self.myactor)
            self.polyline = polyline
            self.tube = tube

        elif key == '2':
            RADIUS = 3.0
            HEIGHT = 10.0
            self.full_mesh.compute_normals()
            for pt in self.polyline.points:
                cyl_pt_1 = pt
                cyl_pt_2 = vec_add(pt, [HEIGHT*x for x in get_normal(self.full_mesh, pt)])
                cyl = mega_tube(pt, cyl_pt_2)
                self.add_prop(PolyActor(mesh=cyl, color='white', edge_visibility=False))



app = App()
app.run()