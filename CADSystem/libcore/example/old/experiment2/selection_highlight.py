import vtk
from libcore.mixins import ViewportMixin
from libcore.interact import StyleActorSelection
from libcore.mesh import Mesh
from libcore.display import PolyActor
from libcore.color import random_mesh_color



class App(ViewportMixin):

    def __init__(self):
        super().__init__()
        self.style = StyleActorSelection(on_click=self.actor_click_handle)
        self.original = Mesh('../data/rooster.midres.stl')
        self.actor = PolyActor(self.original, color=random_mesh_color())
        self.add_prop(self.actor)


        # self.parts = [PolyActor(mesh, color=random_mesh_color(), opacity=0.8) for mesh in self.original.split(n_largest=20)]
        # self.add_props(self.parts)
        #
        # self.interactor.AddObserver(vtk.vtkCommand.CharEvent, self.char)
        #
        # self.actor = None
        # self.actor2 = None



    def actor_click_handle(self, prop, button):
        if button == 'left':
            if not prop.is_selected:
                prop.is_selected = True
                prop.diffuse = 0.8
                prop.ambient = 0.5
                prop.specular = 0.5
                prop.specular_power = 50.0
        if button == 'right':
            if prop.is_selected:
                prop.ambient = 0.0
                prop.diffuse = 1.0
                prop.specular = 0.0
                prop.specular_power = 0.0
                prop.is_selected = False
        if button == 'middle':
            self.remove_prop(prop)
            idx = self.parts.index(prop)
            del self.parts[idx]


app = App()
app.run()
