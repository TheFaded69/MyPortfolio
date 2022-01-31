import vtk
from libcore.mixins import ViewportMixin
from libcore.interact import StyleActorSelection
from libcore.mesh import Mesh
from libcore.display import PolyActor
from libcore.image import Image
from libcore.color import random_color

class App(ViewportMixin):

    def __init__(self):
        super().__init__()
        self.style = StyleActorSelection(on_click=self.actor_click_handle)

        self.original = Mesh('../data/rooster.midres.stl')
        self.parts = [PolyActor(mesh, color=random_color()) for mesh in self.original.split(n_largest=20)]
        self.add_props(self.parts)

        self.register_callback(vtk.vtkCommand.CharEvent, self.on_char)
        self.interactor.AddObserver(vtk.vtkCommand.CharEvent, self.callback)

    def callback(self, caller, event):
        if self.interactor.GetKeySym() == 'a':
            if isinstance(self.interactor.GetInteractorStyle(), vtk.vtkInteractorStyleTrackballCamera):
                self.interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballActor)
            else:
                self.interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera)

    def on_char(self, caller, event):
        key = self.interactor.GetKeySym()
        if key == '1':
            for prop in self.parts:
                prop.mesh.fill_holes(inplace=True)
                print('filling holes')

        self.rwindow.Render()


    def actor_click_handle(self, prop, button):
        if button == 'left':
            if not prop.is_selected:
                prop.is_selected = True
                prop.old_color = prop.color
                prop.color = 'white'
        if button == 'right':
            if hasattr(prop, 'old_color') and prop.is_selected:
                prop.color = prop.old_color
                prop.is_selected = False
        if button == 'middle':
            self.remove_prop(prop)
            idx = self.parts.index(prop)
            del self.parts[idx]


app = App()
app.run()
