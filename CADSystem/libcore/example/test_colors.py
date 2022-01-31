import time

import vtk

from libcore import Mesh
from libcore.mixins import ViewportMixin
from libcore.display import PolyActor
from libcore.color import get_color
from libcore.color import random_mesh_color


# colors = ((0.498, 1.0, 0.831),
#           (0.0, 0.498, 1.0),
#           (0.89, 0.811, 0.341),
#           (0.961, 0.961, 0.863),
#           (0.0, 0.0, 1.0),
#           (0.275, 0.275, 0.275),
#           (0.863, 0.078, 0.235),
#           (0.0, 1.0, 1.0),
#           (0.133, 0.545, 0.133),
#           (1.0, 0.467, 1.0),
#           (1.0, 0.843, 0.0),
#           (0.502, 0.502, 0.502),
#           (0.0, 0.502, 0.0),
#           (0.988, 0.059, 0.753),
#           (0.294, 0.0, 0.51),
#           (1.0, 1.0, 0.941),
#           (0.765, 0.69, 0.569),
#           (0.0, 0.196, 0.588),
#           (1.0, 0.588, 0.157),
#           (0.749, 1.0, 0.0),
#           (0.502, 0.0, 0.0),
#           (0.0, 0.0, 0.804),
#           (0.0, 0.0, 0.502),
#           (0.502, 0.502, 0.0),
#           (1.0, 0.647, 0.0),
#           (0.2, 0.631, 0.788),
#           (0.518, 0.192, 0.475),
#           (0.8, 0.533, 0.6),
#           (1.0, 0.0, 0.0),
#           (0.031, 0.298, 0.62),
#           (0.98, 0.502, 0.447),
#           (0.753, 0.753, 0.753),
#           (0.824, 0.706, 0.549),
#           (0.0, 0.502, 0.502),
#           (1.0, 0.388, 0.278),
#           (0.71, 0.494, 0.863),
#           (0.961, 0.871, 0.702),
#           (1.0, 1.0, 0.0))

# new_colors = ((1.0, 1.0, 1.0))

colors = ((1.0, 1.0, 1.0),
          (1.0, 0.0, 0.0),
          (0.0, 1.0, 0.0),
          (0.0, 0.0, 1.0),
          (1.0, 1.0, 0.0),
          (0.0, 1.0, 1.0),
          (1.0, 0.0, 1.0),
          (0.6, 0.6, 0.6),
          (0.6, 0.0, 0.0),
          (0.0, 0.6, 0.0),
          (0.0, 0.0, 0.6),
          (0.6, 0.6, 0.0),
          (0.0, 0.6, 0.6),
          (0.8, 0.4, 0.4),
          (0.4, 0.8, 0.4),
          (0.4, 0.4, 0.8),
          (0.8, 0.8, 0.4),
          (0.8, 0.4, 0.8),
          (0.4, 0.8, 0.8),
          (0.0, 0.8, 0.4),
          (0.4, 0.0, 0.8),
          (0.8, 0.0, 0.4))

class App(ViewportMixin):

    def __init__(self):
        super().__init__()

        self.mesh = Mesh.sphere()
        color = (0.498, 1.0, 0.831)
        self.actor = PolyActor(mesh=self.mesh, color=get_color(color))
        self.add_prop(self.actor)
        self.register_callback(vtk.vtkCommand.CharEvent, self.call)

    def call(self, caller, event):
        for color in colors:
            self.actor.color = color
            self.rwindow.Render()
            time.sleep(0.5)


if __name__ == '__main__':
    app = App()
    app.run()