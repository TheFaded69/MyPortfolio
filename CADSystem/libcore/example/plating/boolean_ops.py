import vtk
from libcore import Mesh
from libcore.mixins import ViewportMixin
from libcore.display import PolyActor

class App(ViewportMixin):

    def __init__(self):
        super().__init__()

        self.window.SetSize(1024, 800)
        self.style = vtk.vtkInteractorStyleTrackballActor()

        self.sphere1 = Mesh.sphere(center=(-1, 0, 0), radius=2.0)
        self.sphere2 = Mesh.sphere(center=(0, 0, 0), radius=2.5)
        self.sphere1.boolean_difference(self.sphere2, inplace=True)
        print(self.sphere1)
        self.sphere1.reconstruct_surface(inplace=True)
        print(self.sphere1)

        self.actor = PolyActor(self.sphere1, color='blue', edge_visibility=True, edge_color='black', line_width=1.0, opacity=1.0)
        self.add_prop(self.actor)

app = App()
app.run()
