import math

import vtk

from libcore.mesh import Mesh
from libcore.display import PolyActor
from libcore.mixins import ViewportMixin
from libcore.widget import SphereWidget
from libcore.geometry import point_distance, vec_normalize, vec_norm, vec_subtract, vec_cross, vec_dot, vec_add
from libcore.topology import points_ids_within_radius

def point_distance(p1, p2):
    x0, y0, z0 = p1
    x1, y1, z1 = p2
    return abs(x0-x1)+abs(y0-y1)+abs(z0-z1)

def mesh_inflate(mesh, center, radius):
    points = mesh.points
    if mesh.normals is None:
        mesh.compute_normals()
    normals = mesh.normals

    sphere = Mesh.sphere(center=center, radius=radius)

    warp_vectors = [list([0.0, 0.0, 0.0]) for idx in range(mesh.number_of_points)]
    enclosed_indexes = points_ids_within_radius(mesh=mesh, coord=center, radius=radius)

    print(mesh.normals[enclosed_indexes])
    mega_normal = [0.0, 0.0, 0.0]
    for idx in enclosed_indexes:
        mega_normal = vec_add(mega_normal, normals[idx])
    mega_normals = vec_normalize(mega_normal)

    for idx in enclosed_indexes:
        warp_vectors[idx] = [n*radius for n in mega_normal]

        normal = normals[idx]

        # max_distance = 1000000
        # max_idx = 0
        # for i in range(sphere.number_of_points):
        #     distance = point_distance(mesh_point, sphere.points[i])
        #     if distance > max_distance:
        #         max_distance = distance
        #         max_idx = i
        #
        # direction = vec_subtract(mesh_point, sphere.points[max_idx])
        #warp_vectors[idx] = direction


        #max_point = sphere.points[i]


        # normal = normals[idx]


        # print('center: {} \t\t idx: {}\t\tpt: {}\t\tnorm: {}\t\t {}'.format(center, idx, point, normal, vec_norm(normal)))
        #
        # distance = point_distance(point, center)
        # direction = vec_subtract(center, point)
        # vec = [distance*n for n in vec_normalize(vec_cross(normal, direction))]

    mesh.warp(vecs=warp_vectors, inplace=True)
    return mesh


def mesh_deflate(mesh, center, radius):
    points = mesh.points
    if mesh.normals is None:
        mesh.compute_normals()
    normals = mesh.normals

    warp_vectors = [[0.0, 0.0, 0.0] for idx in range(mesh.number_of_points)]
    enclosed_indexes = points_ids_within_radius(mesh=mesh, coord=center, radius=radius)
    for idx in enclosed_indexes:
        point = points[idx]
        normal = normals[idx]

        distance = point_distance(point, center)
        direction = vec_subtract(point, center)
        vec = [distance*radius*n for n in direction]
        warp_vectors[idx] = list(direction)

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

    def callback(self):
        print('Sphere widget was moved, bitches!')

    def on_char(self, caller, event):
        ch = self.interactor.GetKeySym()
        if ch == '1':
            self.actor.mesh = mesh_inflate(mesh=self.mesh, center=self.widget.center, radius=self.widget.radius)
        elif ch == '2':
            self.actor.mesh = mesh_deflate(mesh=self.mesh, center=self.widget.center, radius=self.widget.radius)

        self.rwindow.Render()


app = App()
app.run()