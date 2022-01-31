import vtk

from libcore.mesh import Mesh
from libcore.display import PolyActor
from libcore.mixins import ViewportMixin

class App(ViewportMixin):

    def __init__(self):
        super().__init__()

        sphere = Mesh.sphere(radius=0.8, center=(-1, 0, 0))
        cube = Mesh.cube()

        print('Input sphere has:', sphere.number_of_points)
        print('Input cube has:', cube.number_of_points)

        union = sphere.boolean_intersection(sphere, cube)
        print('Union before cleaning has:', union.number_of_points)
        union.clean(inplace=True)
        print('Union after cleaning has:', union.number_of_points)

        self.actor1 = PolyActor(mesh=sphere, color='blue', opacity=0.8)
        self.actor2 = PolyActor(mesh=cube, color='green', opacity=0.8)
        # self.actor3 = PolyActor(mesh=union, color='white', opacity=0.8)
        self.add_props([self.actor1, self.actor2])

app = App()
app.run()