import vtk
import numpy as np

from libcore.mesh import Mesh
from libcore.mixins import ViewportMixin
from libcore.display import PolyActor


class App(ViewportMixin):

    def __init__(self):
        super().__init__()

        self.mesh1 = Mesh('../../data/rooster.midres.stl')
        self.mesh2 = Mesh.sphere(center=(105.202, 19.188, 101.999), radius=30.0)
        self.mesh_result = self.mesh1.slice_by_mesh(self.mesh2)

        self.actor1 = PolyActor(mesh=self.mesh1,
                                color='white',
                                edge_color='black',
                                edge_visibility=True,
                                opacity=0.2)

        self.actor2 = PolyActor(mesh=self.mesh2,
                                color='yellow',
                                edge_color='black',
                                edge_visibility=True,
                                opacity=0.2)

        self.actor_result = PolyActor(mesh=self.mesh_result,
                                      color='peacock',
                                      render_lines_as_tubes=True,
                                      line_width=5.0,
                                      opacity=1.0)

        self.add_prop(self.actor1)
        self.add_prop(self.actor2)
        self.add_prop(self.actor_result)
        self.look_sup()

if __name__ == '__main__':
    app = App()
    app.run()