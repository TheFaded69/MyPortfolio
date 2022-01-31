# Построение пластинки
import vtk
import math

from libcore.mixins import ViewportMixin
from libcore.display import PolyActor
from libcore.mesh import Mesh

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

        self.skull_mesh = Mesh('pet_1.stl')
        self.implant_mesh = Mesh('pet_2.stl')
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
            polyline = self.curve_widget.points
            tube = make_ribbon(polyline, width=3.0)
            tube = normal_extrude(tube, length=10.0)

            self.myactor = PolyActor(mesh=tube, color='blue', opacity=0.3)
            self.add_prop(self.myactor)

        elif key == '2':
            print('2')


app = App()
app.run()