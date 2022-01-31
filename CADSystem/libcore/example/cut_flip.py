# import vtk
#
# from libcore.mixins import ViewportMixin
# from libcore.display import PolyActor
# from libcore.mesh import Mesh
#
# if __name__ == '__main__':
#     files = ['1.stl']
#
#     for file in files:
#         print('load {}'.format(file))
#         mesh = Mesh('data/{}'.format(file))
#         mesh2 = mesh.reflect(plane='x')
#         print('save {}'.format(file))
#         mesh2.save('out/{}'.format(file))

import vtk
from libcore.mesh import Mesh
from libcore.display import PolyActor
from libcore.mixins import ViewportMixin
from libcore.widget import PlaneSelector
from libcore.geometry import Plane
from libcore.geometry import Plane, point_distance
from libcore.topology import delete_cells, extract_cells_using_points


class App(ViewportMixin):

    def __init__(self):
        super().__init__()

        self.style = vtk.vtkInteractorStyleTrackballCamera()
        self.mesh = Mesh('stich_model.stl')
        self.actor = PolyActor(self.mesh)
        self.add_prop(self.actor)
        self.plane_selector = PlaneSelector(self.interactor, Plane(origin=self.mesh.center, normal=(1, 0, 0)), self.mesh.bounds)
        self.plane_selector.show()
        self.register_callback(vtk.vtkCommand.CharEvent, self.event)

    def event(self, caller, ev):
        key = self.interactor.GetKeySym()
        if key == 'a':
            self.left, self.right = self.mesh.disect_by_plane(self.plane_selector.plane)

            self.left.reflect(plane='x', inplace=True)
            self.left_actor = PolyActor(mesh=self.left, color='blue', opacity=0.5)
            self.right_actor = PolyActor(mesh=self.right, color='red', opacity=0.5)
            delta = self.mesh.min_x - self.left.min_x

            self.left.move(dx=-delta, dy=0, dz=0, inplace=True)

            good_points_indexes = []
            for idx, pt in enumerate(self.right.points):
                closest_idx = self.left.find_closest_point(point=pt)
                closest_pt = self.left.points[closest_idx]
                distance = point_distance(pt, closest_pt)
                if distance > 5.0:
                    good_points_indexes.append(idx)

            result = extract_cells_using_points(self.right, good_points_indexes)
            result.extract_largest(inplace=True)
            result.save('stitch_model_mirrored.stl')
            self.result_actor = PolyActor(mesh=result, color='white')
            self.add_props([self.left_actor, self.right_actor, self.result_actor])

app = App()
app.run()
