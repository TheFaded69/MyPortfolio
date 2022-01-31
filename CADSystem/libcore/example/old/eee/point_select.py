import vtk

from libcore.display import PolyActor
from libcore.mesh import Mesh
from libcore.mixins import ViewportMixin

class LineProbe(object):

    def __init__(self, interactor, prop, on_changed=None):
        self.interactor = interactor
        self.on_changed = on_changed

        self.widget = vtk.vtkLineWidget()
        self.widget.SetInteractor(self.interactor)
        self.widget.SetProp3D(prop)
        self.widget.AddObserver(vtk.vtkCommand.EndInteractionEvent, self.callback)

    def place(self, bounds):
        self.widget.PlaceWidget(bounds)

    def place_at_point(self, pt):
        x, y, z = pt
        self.widget.SetPoint1(x-0.1, y-0.1, z)
        self.widget.SetPoint2(x+0.1, y+0.1, z)

    def as_polydata(self):
        tmp = Mesh()
        self.widget.GetPolyData(tmp)
        return tmp

    def set_on_angle_changed(self, callback):
        self.on_changed = callback

    def callback(self, caller, event):
        spline = vtk.vtkSplineFilter()
        spline.SetInputData(self.as_polydata())
        spline.SetSubdivideToSpecified()
        spline.SetNumberOfSubdivisions(256)
        spline.Update()

        sample_volume = vtk.vtkProbeFilter()
        sample_volume.SetInputData(1, self.image)
        sample_volume.SetInputData(0, spline.GetOutput())
        sample_volume.Update()
        samples = sample_volume.GetOutput().GetPointData().GetArray(0)
        samples = np.array([samples.GetValue(i) for i in range(samples.GetNumberOfValues())])
        if self.on_changed:
            self.on_changed(samples)

    def show(self):
        self.widget.On()

    def hide(self):
        self.widget.Off()


class App(ViewportMixin):

    def __init__(self):
        super().__init__()
        self.mesh = Mesh('../../data/rooster.midres.stl')
        self.actor = PolyActor(self.mesh, color='red')
        self.add_prop(self.actor)

        world_pos = [-0.03, 0.2, -0.05]
        self.handle_rep = vtk.vtkPointHandleRepresentation3D()
        self.handle_rep.SetHandleSize(10)
        self.handle_rep.SetWorldPosition(world_pos)

        self.widget = vtk.vtkHandleWidget()
        self.widget.SetInteractor(self.interactor)
        self.widget.SetRepresentation(self.handle_rep)
        self.widget.EnabledOn()
        


app = App()
app.run()