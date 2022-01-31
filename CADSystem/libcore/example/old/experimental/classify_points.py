import vtk
import numpy as np

from libcore import Mesh
from libcore.geometry import vec_normalize
from libcore.mixins import ViewportMixin
from libcore.geometry import Plane
from libcore.display import PolyActor
from libcore.widget import PlaneSelector



class App(ViewportMixin):

    def __init__(self):
        super().__init__()
        self.mesh = Mesh('../../data/rooster.midres.stl')
        self.plane = Plane(origin=self.mesh.center,
                           normal=vec_normalize([1.0, 0.0, 0.0]))

        print('Center : ', self.mesh.center)

        self.left, self.right = self.mesh.disect_by_plane(self.plane)
        self.result = Mesh(self.right)
        self.result.reflect_around_plane(plane=self.plane)

        self.left_actor = PolyActor(self.left, color='red', opacity=0.5)
        self.add_prop(self.left_actor)
        self.right_actor = PolyActor(self.right, color='green', opacity=0.5)
        self.add_prop(self.right_actor)
        self.result_actor = PolyActor(self.result, color='blue', opacity=0.5)
        self.add_prop(self.result_actor)




if __name__ == '__main__':
    app = App()
    app.run()
