# Нужно сделать нормальный закон изменения меша (на основе гауссиана)
# Нужно

import vtk
import numpy as np

from libcore.mixins import ViewportMixin
from libcore.display import PolyActor
from libcore.mesh import Mesh, square_warp
from libcore.widget import ArrowProbe
from libcore.interact import CircleSelection
from libcore.geometry import vec_add, vec_normalize, vec_norm
from libcore.geometry import point_distance


class App(ViewportMixin):

    def __init__(self):
        super().__init__()
        self.mesh = Mesh('../../data/rooster.midres.stl')
        self.mesh.compute_normals()

        self.actor = PolyActor(mesh=self.mesh, color='red', edge_visibility=True)
        self.add_prop(self.actor)
        self.style = CircleSelection(interactor=self.interactor, on_selected=self.on_selected)
        self.style.set_mesh(self.mesh)
        self.arrow = ArrowProbe(interactor=self.interactor, origin=(0.0, 0, 0.0), on_changed=None)

        self.register_callback(vtk.vtkCommand.CharEvent, self.callback)

    def on_selected(self, center, indexes):
        self.arrow.point1 = center

        self.arrow.point2 = list(np.array(center) + 10*self.mesh.normals[self.mesh.find_closest_point(center)])
        self.arrow.show()
        self.rwindow.Render()

    def callback(self, caller, event):
        square_warp(self.mesh,
                    self.style.selection_indexes,
                    center=self.arrow.point1,
                    direction=self.arrow.direction,
                    length=self.arrow.length)
        self.arrow.hide()
        self.remove_prop(self.style.selection_actor)
        self.style.selection_actor = None
        self.style.set_mesh(self.mesh)
        self.rwindow.Render()

app = App()
app.run()