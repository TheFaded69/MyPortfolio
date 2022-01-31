import vtk

from libcore import Mesh
from libcore.display import PolyActor
from libcore.mixins import ViewportMixin
from libcore.topology import find_geodesic

class App(ViewportMixin):

    def __init__(self):
        super().__init__()
        self.mesh = Mesh.cube(width=30.0, height=12.0, depth=12.0, tesselation_level=5)
        self.mesh.move(dx=15.0, dy=6.0, dz=6.0, inplace=True)
        self.mesh_actor = PolyActor(self.mesh, color='white', edge_visibility=True, edge_color='black', opacity=0.25)

        # A - красная
        self.point_a = [0.0, 6.0, 1.0]
        self.point_a_mesh = Mesh.sphere(center=self.point_a, radius=0.5)
        self.point_a_actor = PolyActor(self.point_a_mesh, color='red', opacity=1.0)

        # B - синяя
        self.point_b = [30, 6.0, 11.0]
        self.point_b_mesh = Mesh.sphere(center=self.point_b, radius=0.5)
        self.point_b_actor = PolyActor(self.point_b_mesh, color='blue', opacity=1.0)

        self.point_a_idx = self.mesh.find_closest_point(self.point_a)
        self.point_b_idx = self.mesh.find_closest_point(self.point_b)

        print('Ищем кратчайший путь...')
        self.trajectory = find_geodesic(mesh=self.mesh,
                                        start=self.point_b_idx,
                                        end=self.point_a_idx)

        for i in range(len(self.trajectory.points)):
            print('{}:{}'.format(i, self.trajectory.points[i, :]))

        self.trajectory_actor = PolyActor(self.trajectory, render_lines_as_tubes=True, line_width=3.0, color='green')

        self.add_props([self.mesh_actor,
                        self.point_a_actor,
                        self.point_b_actor,
                        self.trajectory_actor])


app = App()
app.run()