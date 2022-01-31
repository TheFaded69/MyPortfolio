import vtk
from libcore.mesh import Mesh
from libcore.display import PolyActor
from libcore.mixins import ViewportMixin
from libcore.widget import SphereWidget
from libcore.topology import mesh_inflate, mesh_deflate

class App(ViewportMixin):

    def __init__(self):
        super().__init__()
        self.style = vtk.vtkInteractorStyleJoystickCamera()

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