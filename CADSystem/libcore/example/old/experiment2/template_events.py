import vtk



class TemplateInteractorStyle(vtk.vtkInteractorStyle):

    def __init__(self, parent=None):
        self.RemoveAllObservers()
        self.AddObserver("CharEvent", self.on_char_event)
        self.AddObserver("EndInteractionEvent", self.on_end_interaction_event)
        self.AddObserver("KeyPressEvent", self.on_key_press_event)
        self.AddObserver("KeyReleaseEvent", self.on_key_release_event)
        self.AddObserver("LeftButtonPressEvent", self.on_left_button_press_event)
        self.AddObserver("LeftButtonReleaseEvent", self.on_left_button_release_event)
        self.AddObserver("MiddleButtonPressEvent", self.on_middle_button_press_event)
        self.AddObserver("MiddleButtonReleaseEvent", self.on_middle_button_release_event)
        self.AddObserver("MouseMoveEvent", self.on_mouse_move_event)
        self.AddObserver("MouseWheelBackwardEvent", self.on_mouse_wheel_backward_event)
        self.AddObserver("MouseWheelForwardEvent", self.on_mouse_wheel_forward_event)
        self.AddObserver("RightButtonPressEvent", self.on_right_button_press_event)
        self.AddObserver("RightButtonReleaseEvent", self.on_right_button_release_event)
        self.AddObserver("StartInteractionEvent", self.on_start_interaction_event)
        self.AddObserver("EnterEvent", self.on_enter_event)
        self.AddObserver("LeaveEvent", self.on_leave_event)
        self.AddObserver("ExposeEvent", self.on_expose_event)

        self.mesh = None
        self.world_picker = vtk.vtkWorldPointPicker()
        self.cell_picker = vtk.vtkCellPicker()



    @property
    def interactor(self):
        return self.GetInteractor()

    @property
    def renderer(self):
        return self.GetInteractor().GetRenderWindow().GetRenderers().GetFirstRenderer()

    @property
    def camera(self):
        return self.renderer.GetDefaultCamera()

    def pick(self):
        point = self.interactor.GetEventPosition()
        print(point)
        return self.world_picker.Pick(point[0], point[1], 0, self.renderer)


    def on_char_event(self, obj, event):
        print(event)
        print(self.interactor)
        print(self.renderer)

    def on_end_interaction_event(self, obj, event):
        print(event)

    def on_key_press_event(self, obj, event):
        print(event)

    def on_key_release_event(self, obj, event):
        print(event)

    def on_left_button_press_event(self, obj, event):
        print(event)
        self.OnLeftButtonDown()

    def on_left_button_release_event(self, obj, event):
        print(event)
        self.OnLeftButtonUp()

    def on_middle_button_press_event(self, obj, event):
        print(event)
        self.OnMiddleButtonDown()

    def on_middle_button_release_event(self, obj, event):
        print(event)
        self.OnMiddleButtonUp()

    def on_mouse_move_event(self, obj, event):
        print(event)
        self.OnMouseMove()
        print(self.pick())


    def on_mouse_wheel_backward_event(self, obj, event):
        print(event)
        self.OnMouseWheelBackward()

    def on_mouse_wheel_forward_event(self, obj, event):
        print(event)
        self.OnMouseWheelForward()

    def on_right_button_press_event(self, obj, event):
        print(event)
        self.OnRightButtonDown()

    def on_right_button_release_event(self, obj, event):
        print(event)
        self.OnRightButtonUp()

    def on_start_interaction_event(self, obj, event):
        print(event)


    def on_enter_event(self, obj, event):
        print(event)

    def on_leave_event(self, obj, event):
        print(event)

    def on_expose_event(self, obj, event):
        print(event)


src = vtk.vtkSphereSource()
src.SetRadius(1.0)
mapper = vtk.vtkPolyDataMapper()
mapper.SetInputConnection(src.GetOutputPort())
actor = vtk.vtkActor()
actor.SetMapper(mapper)
actor.GetProperty().SetColor(1.0, 0.25, 0.25)

renderer = vtk.vtkRenderer()
window = vtk.vtkRenderWindow()
window.AddRenderer(renderer)
interactor = vtk.vtkRenderWindowInteractor()
style = TemplateInteractorStyle()
interactor.SetInteractorStyle(style)
interactor.SetRenderWindow(window)


def callback(caller, event):
    actor.SetScale(100, 1, 1)
    actor.SetVisibility(0)
    window.Render()


interactor.AddObserver('UserEvent', callback)

renderer.AddActor(actor)
interactor.Start()
