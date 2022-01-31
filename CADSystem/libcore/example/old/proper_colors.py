import vtk
import random
from libcore.mixins import ViewportMixin
from libcore.color import get_color, colors, random_mesh_color
from libcore.mesh import Mesh
from libcore.display import PolyActor


class App(ViewportMixin):

    def __init__(self):
        super().__init__()
        for i in range(300):
            mesh = Mesh.sphere(center=(random.random(), random.random(), random.random()), radius=0.04)
            self.add_prop(PolyActor(mesh, color=random_mesh_color()))

        self.interactor.CreateRepeatingTimer(100)
        self.interactor.AddObserver(vtk.vtkCommand.TimerEvent, self.on_timer)

    def on_timer(self, caller, event):
        print('on timer')
        for actor in self.actors():
            actor.color = random_mesh_color()
        self.rwindow.Render()

if __name__ == '__main__':
    app = App()
    app.run()
