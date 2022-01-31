import vtk

from libcore import Mesh
from libcore.mixins import ViewportMixin
from libcore.geometry import Plane
from libcore.display import PolyActor
from libcore.widget import PlaneSelector


class App(ViewportMixin):

    def __init__(self):
        super().__init__()
        self.mesh = Mesh('../data/111n+.stl')
        self.mesh2 = None
        self.actor = PolyActor(self.mesh, color='white', edge_visibility=True, opacity=1.0)
        self.actor2 = None

        self.add_prop(self.actor)
        self.plane = Plane.XZ(origin=self.mesh.center)
        self.plane_widget = PlaneSelector(self.interactor, self.plane, self.mesh.bounds)
        self.plane_widget.show()
        self.interactor.AddObserver(vtk.vtkCommand.EndInteractionEvent, self.process)

    def process(self, caller, event):
        if self.actor2:
            self.remove_prop(self.actor2)
        self.mesh2 = self.mesh.disect_by_plane(self.plane_widget.plane)
        self.mesh.reflect(plane='x', inplace=True)
        self.actor2 = PolyActor(self.mesh, color='red', edge_visibility=True, opacity=1.0)
        self.add_prop(self.actor2)
        self.rwindow.Render()

if __name__ == '__main__':
    app = App()
    app.run()
