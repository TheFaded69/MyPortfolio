import vtk
from libcore.mesh import Mesh
from libcore.display import PolyActor
from libcore.mixins import ViewportMixin
from libcore.widget import PlaneSelector
from libcore.geometry import Plane

class App(ViewportMixin):

    def __init__(self):
        super().__init__()

        self.style = vtk.vtkInteractorStyleTrackballCamera()
        self.mesh = Mesh('../data/rooster.midres.stl')
        self.actor = PolyActor(self.mesh)
        self.add_prop(self.actor)
        self.plane_selector = PlaneSelector(self.interactor, Plane(origin=self.mesh.center, normal=(1, 0, 0)), self.mesh.bounds)
        self.plane_selector.show()
        self.register_callback(vtk.vtkCommand.CharEvent, self.event)

    def event(self, caller, ev):
        key = self.interactor.GetKeySym()
        if key == 'a':
            print('disect meshes')
            left, right = self.mesh.disect_by_plane(self.plane_selector.plane)
            print('close left mesh')
            left.close_mesh(inplace=True)
            print('close right mesh')
            right.close_mesh(inplace=True)
            self.actor.hide()
            self.plane_selector.hide()
            self.style = vtk.vtkInteractorStyleTrackballActor()
            self.add_prop(PolyActor(left, color='green'))
            self.add_prop(PolyActor(right, color='blue'))
        self.rwindow.Render()

app = App()
app.run()
