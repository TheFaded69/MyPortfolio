import vtk
from libcore import Mesh
from libcore.display import PolyActor
from libcore.mixins import ViewportMixin

class App(ViewportMixin):

    def __init__(self):
        super().__init__()
        style = vtk.vtkInteractorStyleTrackballActor()

        original = Mesh('../data/rooster.midres.stl')
        print(original)
        self.meshes = [original.decimate(algorithm='quadric', reduction=0.5),
                       original.decimate(algorithm='quadric', reduction=0.8),
                       original.decimate(algorithm='quadric', reduction=0.95),
                       original.decimate(algorithm='pro', reduction=0.5),
                       original.decimate(algorithm='pro', reduction=0.8),
                       original.decimate(algorithm='pro', reduction=0.95),
                       original.decimate(algorithm='clustering')]

        colors = ['red', 'green', 'white', 'blue', 'cyan', 'olive', 'violet', 'azure']
        self.actors = []
        for mesh, color in zip(self.meshes, colors):
            print(mesh)
            actor = PolyActor(mesh, color=color, edge_visibility=True, edge_color='black', line_width=1.0, opacity=1.0)
            self.add_prop(actor)

app = App()
app.run()
