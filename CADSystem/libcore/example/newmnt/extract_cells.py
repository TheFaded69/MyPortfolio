# Устранить зазор вокруг извлеченного меша
import vtk

from libcore.mesh import Mesh
from libcore.mixins import ViewportMixin
from libcore.geometry import Plane, point_distance
from libcore.topology import delete_cells, extract_cells_using_points
from libcore.display import PolyActor

class App(ViewportMixin):

    def __init__(self):
        super().__init__()

        self.original = Mesh('../data/rooster.hires.stl')
        self.left_mesh, self.right_mesh = self.original.disect_by_plane(Plane.XZ(origin=self.original.center))
        self.left_mesh.reflect(plane='x', inplace=True)
        self.left_actor = PolyActor(mesh=self.left_mesh, color='blue', opacity=0.5)
        self.right_actor = PolyActor(mesh=self.right_mesh, color='red', opacity=0.5)
        delta = self.original.min_x - self.left_mesh.min_x
        print('delta=')
        print('self.original', self.original.bounds)
        print(self.original.center)

        print('self.left_mesh', self.left_mesh.bounds)
        print(self.left_mesh.center)
        print('self.right_mesh', self.right_mesh.bounds)
        print(self.right_mesh.center)

        self.left_mesh.move(dx=delta, dy=0, dz=0, inplace=True)


        good_points_indexes = []
        for idx, pt in enumerate(self.right_mesh.points):
            closest_idx = self.left_mesh.find_closest_point(point=pt)
            closest_pt = self.left_mesh.points[closest_idx]
            distance = point_distance(pt, closest_pt)
            if distance > 5.0:
                good_points_indexes.append(idx)

        result = extract_cells_using_points(self.right_mesh, good_points_indexes)
        result.extract_largest(inplace=True)
        self.result_actor = PolyActor(mesh=result, color='white')
        #self.add_prop(self.result_actor)
        self.add_props([self.left_actor, self.right_actor, self.result_actor])



if __name__ == '__main__':
    app = App()
    app.run()