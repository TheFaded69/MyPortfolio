import vtk

import vtk
from libcore.mixins import ViewportMixin
from libcore.color import get_color
from libcore.mesh import Mesh
from libcore.display import PolyActor

class App(ViewportMixin):

    def __init__(self):
        super().__init__()
        self.style = vtk.vtkInteractorStyleJoystickActor()
        self.mesh1 = Mesh('../data/compare/76-smooth-min-closed-cups.stl')
        self.mesh2 = Mesh('../data/compare/Shk.stl')

        self.add_prop(PolyActor(self.mesh1, color='red'))
        self.add_prop(PolyActor(self.mesh2, color='white', opacity=0.5))

        self.register_callback(vtk.vtkCommand.CharEvent, self.callback)

    def callback(self, caller, event):
        key = self.interactor.GetKeySym()
        if key == 'a':
            self.renderer.ResetCamera()
            self.zoom(2.0)
        #self.renderer.ResetCamera()
        #self.renderer.Dolly(2.0)

if __name__ == '__main__':
    app = App()
    app.run()
