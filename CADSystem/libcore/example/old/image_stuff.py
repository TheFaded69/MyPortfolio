import vtk
from libcore.image import Image
from libcore.mesh import Mesh
from libcore.mixins import ViewportMixin
from libcore.display import PolyActor
from libcore.widget import ImageView


class App(ViewportMixin):
    def __init__(self):
        super().__init__()
        self.style = vtk.vtkInteractorStyleTrackballCamera()

        self.image = Image()
        self.image.load('../../data/rooster.vti')

        self.image_view = ImageView(self.interactor, self.image)
        self.image_view.on_windowlevel_changed = self.on_windowlevel
        self.image_view.on_cursor_changed = self.on_cursor
        self.image_view.contour_threshold = 200
        self.image_view.show()

        self.image_view.plane_x.SetRightButtonAction(vtk.vtkImagePlaneWidget.VTK_SLICE_MOTION_ACTION)
        self.image_view.plane_x.SetMiddleButtonAction(vtk.vtkImagePlaneWidget.VTK_WINDOW_LEVEL_ACTION)
        self.image_view.plane_y.SetRightButtonAction(vtk.vtkImagePlaneWidget.VTK_SLICE_MOTION_ACTION)
        self.image_view.plane_y.SetMiddleButtonAction(vtk.vtkImagePlaneWidget.VTK_WINDOW_LEVEL_ACTION)
        self.image_view.plane_z.SetRightButtonAction(vtk.vtkImagePlaneWidget.VTK_SLICE_MOTION_ACTION)
        self.image_view.plane_z.SetMiddleButtonAction(vtk.vtkImagePlaneWidget.VTK_WINDOW_LEVEL_ACTION)

        # for d in dir(vtk.vtkImagePlaneWidget):
        #     print(d)

        # VTK_CONTROL_MODIFIER
        # VTK_CURSOR_ACTION
        # VTK_NO_MODIFIER
        # VTK_SHIFT_MODIFIER
        # VTK_SLICE_MOTION_ACTION
        # VTK_WINDOW_LEVEL_ACTION
        #self.image_view.plane_x.GetLeftButtonAction(vtk.vtkImagePlaneWidget)
        #self.add_prop(PolyActor(iso, color='blue', line_width=2.5, render_lines_as_tubes=True))
        self.register_callback(vtk.vtkCommand.CharEvent, self.event)

    def on_windowlevel(self, window, level):
        print('window: ', window)
        print('level: ', level)

    def on_cursor(self, cursor):
        print(cursor)

    def event(self, caller, ev):
        key = self.interactor.GetKeySym()

        if key == 'a':
            self.look_ap()
        elif key == 's':
            self.look_inf()
        elif key == 'd':
            self.look_lao()
        elif key == 'f':
            self.look_ll()
        elif key == 'g':
            self.look_pa()
        elif key == 'h':
            self.look_sup()
        self.rwindow.Render()


app = App()
app.run()