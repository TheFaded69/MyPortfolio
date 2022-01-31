import vtk
from libcore.mesh import Mesh
from libcore.mixins import ViewportMixin
from libcore.widget import CubeSelector

class App(ViewportMixin):

    def __init__(self):
        super().__init__()

        self.style = vtk.vtkInteractorStyleTrackballCamera()
        self.mesh = Mesh('../data/rooster.midres.stl')

        self.cube_selector = CubeSelector(self.interactor, self.mesh)
        self.cube_selector.show()
        self.register_callback(vtk.vtkCommand.CharEvent, self.event)

    def event(self, caller, ev):
        key = self.interactor.GetKeySym()
        if key == '1':
            self.mesh.clip_by_mesh(self.cube_selector.as_polydata(), True, inplace=True)
        elif key == '2':
            self.mesh.clip_by_mesh(self.cube_selector.as_polydata(), False, inplace=True)

        self.rwindow.Render()

app = App()
app.run()
