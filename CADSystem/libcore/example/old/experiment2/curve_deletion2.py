import vtk

from libcore import Mesh
from libcore.geometry import point_distance, vec_normalize
from libcore.display import PolyActor
from libcore.mixins import ViewportMixin
from libcore.interact import StyleDrawPolygon3





class App(ViewportMixin):

    def __init__(self):
        super().__init__()
        self.mesh = Mesh('../data/rooster.midres.stl')
        self.actor = PolyActor(self.mesh, color='blue')
        self.actor2 = None
        self.add_prop(self.actor)

        self.style = StyleDrawPolygon3(interactor=self.interactor, on_select=self.on_end_interaction)

    def on_end_interaction(self, res):
        self.mesh.clip_by_mesh(res, inplace=True)
        self.style = vtk.vtkInteractorStyleTrackball()
        self.rwindow.Render()

app = App()
app.run()