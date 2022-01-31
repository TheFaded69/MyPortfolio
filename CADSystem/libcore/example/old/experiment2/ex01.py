import vtk
import numpy as np
from libcore.mesh import Mesh
from libcore.topology import closest_point_idx
from libcore.mixins import ViewportMixin
from libcore.display import PolyActor
from libcore.geometry import Plane



class App(ViewportMixin):

    def __init__(self):
        super().__init__()

        self.mesh = Mesh.sphere(resolution_theta=3, resolution_phi=18)
        self.actor = PolyActor(self.mesh, color='red', edge_visibility=True)
        self.add_prop(self.actor)

        self.style = vtk.vtkInteractorStyleJoystickActor()
        self.interactor.AddObserver('LeftButtonPressEvent', self.on_left_button_press_event)
        self.interactor.AddObserver('MouseMoveEvent', self.on_cursor_changed)

        self.picker = vtk.vtkWorldPointPicker()
        self.interactor.SetPicker(self.picker)

        self.click_pos = None

    def pick(self):
        pos = self.interactor.GetEventPosition()
        self.picker.Pick(pos[0], pos[1], 0, self.renderer)
        return self.picker.GetPickPosition()


    def on_left_button_press_event(self, caller, event):
        self.click_pos = self.pick()


    def on_cursor_changed(self, caller, event):
        prev_pos = self.click_pos
        pos = self.pick()
        if self.click_pos:
            print('prev: ', prev_pos)
            print('current: ', pos)
            self.click_pos = None

            vec = (pos[0]-prev_pos[0], pos[1]-prev_pos[1], pos[2]-prev_pos[2])
            idx = closest_point_idx(self.mesh, prev_pos)
            self.mesh.points[idx] += vec
            self.mesh.Modified()
            #self.actor.GetMapper().SetInputData(self.mesh)
            print(idx)
            print(vec)


        self.renderer.RemoveActor(self.actor)
        self.actor = PolyActor(self.mesh, color='red', edge_visibility=True)
        self.renderer.AddActor(self.actor)

    def run(self):
        self.interactor.Start()

app = App()
app.run()