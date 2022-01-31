import vtk
from libcore.mixins import ViewportMixin
from libcore.color import get_color
from libcore.mesh import Mesh
from libcore.display import PolyActor

class App(ViewportMixin):

    def __init__(self):
        super().__init__()

        self.actor = PolyActor(Mesh('../../data/rooster.midres.stl'))
        self.add_prop(self.actor)

        self.handle_widget = vtk.vtkHandleWidget()
        self.handle_widget.SetInteractor(self.interactor)
        self.handle_widget.On()

        self.interactor.AddObserver(vtk.vtkCommand.CharEvent, self.callback)

    def callback(self, caller, event):
        if self.interactor.GetKeySym() == 'a':
            print(type(self.interactor.GetInteractorStyle()))
            if isinstance(self.interactor.GetInteractorStyle(), vtk.vtkInteractorStyleTrackballCamera):
                self.interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballActor())
                print('set actor')
            else:
                self.interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
                print('set camera')

if __name__ == '__main__':
    app = App()
    app.run()
