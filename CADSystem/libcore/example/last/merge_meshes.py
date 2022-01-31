# Сделать объединение данных двух мешей путем
# их конвертирования в structured grid или unstructured grid

import vtk
from libcore.mixins import ViewportMixin
from libcore.mesh import Mesh
from libcore.display import PolyActor
from libcore.topology import delaunay_surface

class App(ViewportMixin):

    def __init__(self):
        super().__init__()
        self.style = vtk.vtkInteractorStyleJoystickCamera()

        print('Load mesh')
        mesh = Mesh('../data/rooster.lowres.stl')
        print('Extract largest mesh')
        mesh.extract_largest(inplace=True)
        sphere1 = Mesh.sphere(center=(96, 106, 35), radius=30.0)
        sphere2 = Mesh.sphere(center=(136, 106, 35), radius=30.0)
        print('Create meshes')
        sphere = Mesh.from_meshes([sphere1, sphere2])
        print('Clip by mesh')
        region = mesh.clip_by_mesh(sphere)

        self.mesh_actor = PolyActor(mesh, color='blue', opacity=0.1)
        self.sphere_actor = PolyActor(sphere, color='white', opacity=0.1)
        self.region_actor = PolyActor(region, color='red', opacity=1.0)
        self.convex_hull_actor = PolyActor(delaunay_surface(mesh), opacity=0.5)
        self.add_props([self.mesh_actor, self.sphere_actor, self.region_actor, self.convex_hull_actor])
        self.register_callback(vtk.vtkCommand.CharEvent, self.event)

    def event(self, caller, ev):
        key = self.interactor.GetKeySym()
        if key == '1':
            if self.mesh_actor.is_visible:
                self.mesh_actor.hide()
            else:
                self.mesh_actor.show()
        elif key == '2':
            if self.sphere_actor.is_visible:
                self.sphere_actor.hide()
            else:
                self.sphere_actor.show()
        elif key == '3':
            if self.region_actor.is_visible:
                self.region_actor.hide()
            else:
                self.region_actor.show()
        elif key == '4':
            if self.convex_hull_actor.is_visible:
                self.convex_hull_actor.hide()
            else:
                self.convex_hull_actor.show()
        self.rwindow.Render()


app = App()
app.run()
