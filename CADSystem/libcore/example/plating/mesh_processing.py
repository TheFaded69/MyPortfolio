import vtk
from libcore import Mesh
from libcore.display import PolyActor
from libcore.mixins import ViewportMixin

class App(ViewportMixin):

    def __init__(self):
        super().__init__()
        style = vtk.vtkInteractorStyleTrackballActor()

        sphere = Mesh.sphere(radius=2.0, center=(-1.0, 0, 0))
        torus = Mesh.torus()
        original = sphere.boolean_union(torus)
        print(original)
        self.meshes = [original.decimate(algorithm='quadric', reduction=0.5),
                       original.decimate(algorithm='pro', reduction=0.5),
                       original.decimate(algorithm='clustering'),
                       original.smooth(iterations=10),
                       original.reconstruct_surface(),
                       original.subdivide(algorithm='linear'),
                       original.subdivide(algorithm='butterfly'),
                       original.subdivide(algorithm='loop')]

        colors = ['red', 'green', 'white', 'blue', 'yellow', 'orange', 'plum', 'cyan', 'olive', 'violet', 'azure']
        self.actors = []
        for mesh, color in zip(self.meshes, colors):
            print(mesh)
            actor = PolyActor(mesh, color=color, edge_visibility=True, edge_color='black', line_width=1.0, opacity=1.0)
            self.add_prop(actor)

app = App()
app.run()
