

import vtk

from libcore.mesh import Mesh
from libcore.mixins import ViewportMixin
from libcore.display import PolyActor
from libcore.widget import CubeManipulator

class App(ViewportMixin):

    def __init__(self):
        super().__init__()

        self.style = vtk.vtkInteractorStyleTrackballCamera()

        self.skull_mesh = Mesh('../../data/rooster.midres.stl')
        self.skull_actor = PolyActor(mesh=self.skull_mesh, color='red')

        self.sphere_mesh = Mesh.sphere(center=(105.202, 99.188, 50.0), radius=30.0)
        self.sphere_actor = PolyActor(mesh=self.sphere_mesh, color='blue', opacity=0.5)

        self.widget = CubeManipulator(interactor=self.interactor, actor=self.sphere_actor)
        self.widget.show()

        self.result = None

        self.add_prop(self.skull_actor)
        self.add_prop(self.sphere_actor)

        self.register_callback(vtk.vtkCommand.CharEvent, self.on_char)



    def on_char(self, caller, event):
        if self.result:
            self.remove_prop(self.result)

        result_mesh = self.skull_mesh.clip_by_mesh(self.widget.mesh)
        self.result = PolyActor(mesh=result_mesh, color='yellow')
        self.add_prop(self.result)
        print(self.widget.mesh)


if __name__ == '__main__':
    app = App()
    app.run()