мimport vtk
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
        self.interactor.AddObserver('LeftButtonReleaseEvent', self.on_left_button_release_event)
        self.interactor.AddObserver('MouseMoveEvent', self.on_cursor_changed)

        self.pressed = False


    def on_left_button_press_event(self, caller, event):
        print('Pressed!')
        self.pressed = True
        #self.interactor.GetInteractorStyle().OnLef

    def on_left_button_release_event(self, caller, event):
        self.pressed = False

    def on_cursor_changed(self, caller, event):
        if self.pressed:
            pos = self.interactor.GetEventPosition()
            picker = vtk.vtkCellPicker()
            picker.SetTolerance(0.0005)

            # Pick from this location.
            picker.Pick(pos[0], pos[1], 0, self.renderer)

            world_position = picker.GetPickPosition()
            cell = picker.GetCellId()
            print(cell)
            delete_cells(self.mesh, [cell])

        self.renderer.RemoveActor(self.actor)
        self.actor = make_actor(self.mesh)
        self.renderer.AddActor(self.actor)

    def run(self):
        self.interactor.Start()

app = App()
app.run()