from random import random

import vtk

from libcore.mesh import Mesh
from libcore.display import PolyActor
from libcore.mixins import ViewportMixin

class App(ViewportMixin):

    def __init__(self):
        super().__init__()

        self.mesh = Mesh.sphere()

        vecs = []
        for i in range(self.mesh.number_of_points):
            vecs.append((0.1*random(), 0.1*random(), 0.1*random()))

        self.mesh.warp(self.mesh, inplace=True)

        self.actor = PolyActor(mesh=self.mesh, color='red')
        self.add_prop(self.actor)

app = App()
app.run()