import math

import vtk

from libcore.mesh import Mesh
from libcore.display import PolyActor
from libcore.mixins import ViewportMixin
from libcore.widget import SphereWidget
from libcore.geometry import point_distance, vec_normalize, vec_norm, vec_subtract, vec_cross, vec_dot, vec_add
from libcore.topology import points_ids_within_radius

def mesh_inflate(mesh, center, radius, direction):
    points = mesh.points
    if mesh.normals is None:
        mesh.compute_normals()
    normals = mesh.normals

    warp_vectors = [list([0.0, 0.0, 0.0]) for idx in range(mesh.number_of_points)]
    enclosed_indexes = points_ids_within_radius(mesh=mesh, coord=center, radius=radius)
    for idx in enclosed_indexes:
        vec = [radius*n for n in direction]
        warp_vectors[idx] = list(vec)

    mesh.warp(vecs=warp_vectors, inplace=True)
    return mesh


class App(ViewportMixin):

    def __init__(self):
        super().__init__()
        self.style = vtk.vtkInteractorStyleTrackball()

        self.mesh = Mesh('../../data/rooster.midres.stl')
        self.mesh.compute_normals()
        self.actor = PolyActor(mesh=self.mesh, color='blue')
        self.add_prop(self.actor)

        self.widget = SphereWidget(interactor=self.interactor)
        self.widget.show()

        self.register_callback(vtk.vtkCommand.CharEvent, self.on_char)

    def on_char(self, caller, event):
        ch = self.interactor.GetKeySym()
        if ch == '1':
            self.actor.mesh = mesh_inflate(mesh=self.mesh, center=self.widget.center, radius=self.widget.radius, direction=self.widget.direction)

        self.rwindow.Render()


app = App()
app.run()