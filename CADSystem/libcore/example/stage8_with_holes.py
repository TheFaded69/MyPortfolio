# Сделать полосу с правильными нормалями?


# Построение пластинки
import numpy as np
import vtk
import math

from libcore.mixins import ViewportMixin
from libcore.display import PolyActor
from libcore.mesh import Mesh
from libcore.geometry import vec_add

def make_ribbon(polyline, width=2.0):
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
            polyline = self.curve_widget.points
            # normals = [self.full_mesh.normals[self.full_mesh.find_closest_point(pt)] for pt in polyline.points]
            # polyline.normals = normals


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



# class App(ViewportMixin):
#
#     def __init__(self):
#         super().__init__()
#
#         self.mesh1 = Mesh('pet_2.stl')
#         self.mesh1.fill_holes(hole_size=10, inplace=True)
#         self.mesh1.close_mesh(inplace=True)
#
#         self.mesh_add1 = Mesh.cylinder(center=(156, 51, 80), radius=10.0)
#         self.mesh_add2 = Mesh.cylinder(center=(116, 51, 80), radius=6.0)
#
#         self.mesh_sub1 = Mesh.cylinder(center=(136, 71, 90), radius=15.0)
#         self.mesh_sub2 = Mesh.cylinder(center=(136, 21, 70), radius=10.0)
#
#         self.result_mesh = implicitly_combine(main=self.mesh1,
#                                               to_add_list=[self.mesh_add1, self.mesh_add2],
#                                               to_subtract_list=[self.mesh_sub1, self.mesh_sub2])
#
#         # self.mesh1 = implicitize(self.mesh1)
#         # self.mesh1.fill_holes(hole_size=10, inplace=True)
#         # self.mesh1.close_mesh(inplace=True)
#         # self.mesh1.extract_largest(inplace=True)
#
#         # self.random_mesh = delaunay_surface(gen_random_pc(num_points=200, radius=1.0))
#         self.actor = PolyActor(mesh=self.result_mesh)
#         self.add_prop(self.actor)


app = App()
app.run()