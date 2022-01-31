import vtk

from libcore.mixins import ViewportMixin
from libcore.display import PolyActor
from libcore.mesh import Mesh


class App(ViewportMixin):

    def __init__(self):
        super().__init__()

        # self.mesh = Mesh('../../data/rooster.midres.stl')
        # self.actor = PolyActor(mesh=self.mesh, color='red')
        # self.add_prop(self.actor)

        self.spline_widget = vtk.vtkSplineWidget2()
        self.spline_widget.SetInteractor(self.interactor)

        self.register_callback(vtk.vtkCommand.CharEvent, self.callback)

    def callback(self, caller, event):
        self.spline_widget.On()


app = App()
app.run()