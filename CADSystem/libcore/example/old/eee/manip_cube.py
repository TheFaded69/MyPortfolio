import vtk

from libcore.display import PolyActor
from libcore.mesh import Mesh
from libcore.mixins import ViewportMixin
from libcore.widget import CubeManipulator

class App(ViewportMixin):

    def __init__(self):
        super().__init__()
        self.ident = vtk.vtkTransform()
        self.ident.Identity()

        self.mesh_sphere = Mesh.sphere(center=(30, 0, 0), radius=20.0, resolution_theta=51, resolution_phi=51)
        self.actor_sphere = PolyActor(self.mesh_sphere, color='red')
        self.mesh_cube = Mesh.cube(width=10.0, height=10.0, depth=10.0)
        self.actor_cube = PolyActor(self.mesh_cube, color='green')

        self.add_props([self.actor_sphere,
                        self.actor_cube])

        self.manip_sphere = CubeManipulator(interactor=self.interactor, actor=self.actor_sphere)
        self.manip_cube = CubeManipulator(interactor=self.interactor, actor=self.actor_cube)

        self.manip_sphere.show()
        self.manip_cube.show()

        self.register_callback(vtk.vtkCommand.CharEvent, self.on_char)

    def on_char(self, caller, event):
        char = self.interactor.GetKeySym()
        if char == '1':
            self.manip_sphere.hide()
            self.add_prop(PolyActor(self.manip_sphere.mesh, color='yellow'))
            self.rwindow.Render()
        elif char == '2':
            self.manip_cube.hide()
            self.add_prop(PolyActor(self.manip_cube.mesh, color='blue'))
            self.rwindow.Render()


app = App()
app.run()