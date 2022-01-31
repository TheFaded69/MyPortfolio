import vtk
import numpy as np
from coco import Mesh
from coco.util import *



class App(object):

    def __init__(self):
        self.renderer = vtk.vtkRenderer()
        self.window = vtk.vtkRenderWindow()
        self.interactor = vtk.vtkRenderWindowInteractor()

        self.window.AddRenderer(self.renderer)
        self.window.SetSize(1024, 800)
        self.interactor.SetRenderWindow(self.window)
        self.interactor.Initialize()

        self.mesh = Mesh.sphere()
        self.actor = make_actor(self.mesh)

        self.renderer.AddActor(self.actor)

        self.interactor.SetInteractorStyle(vtk.vtkInteractorStyleJoystickActor())
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
        self.actor = make_actor(self.mesh)
        self.renderer.AddActor(self.actor)

    def run(self):
        self.interactor.Start()

app = App()
app.run()