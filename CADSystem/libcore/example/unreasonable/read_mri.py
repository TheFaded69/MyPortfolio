import vtk
from libcore.mixins import ViewportMixin
from libcore.widget import ImageView

from libcore.dicom import load_directory

MRI_DIR = '../../data/dicom/mri'
CT_DIR = '../../data/dicom/rooster/'

class App(ViewportMixin):
    def __init__(self):
        super().__init__()
        self.style = vtk.vtkInteractorStyleTrackballCamera()

        self.image = load_directory(MRI_DIR)
        print(self.image.min_value, self.image.max_value)
        print(self.image)
        print(self.image.modality)
        print(self.image.is_ct())
        print(self.image.is_mri())

        self.image_view = ImageView(self.interactor, self.image, contour_threshold=50)
        self.image_view.on_windowlevel_changed = self.on_windowlevel
        self.image_view.on_cursor_changed = self.on_cursor
        self.image_view.show()

        self.image_view.plane_x.SetRightButtonAction(vtk.vtkImagePlaneWidget.VTK_SLICE_MOTION_ACTION)
        self.image_view.plane_x.SetMiddleButtonAction(vtk.vtkImagePlaneWidget.VTK_WINDOW_LEVEL_ACTION)
        self.image_view.plane_y.SetRightButtonAction(vtk.vtkImagePlaneWidget.VTK_SLICE_MOTION_ACTION)
        self.image_view.plane_y.SetMiddleButtonAction(vtk.vtkImagePlaneWidget.VTK_WINDOW_LEVEL_ACTION)
        self.image_view.plane_z.SetRightButtonAction(vtk.vtkImagePlaneWidget.VTK_SLICE_MOTION_ACTION)
        self.image_view.plane_z.SetMiddleButtonAction(vtk.vtkImagePlaneWidget.VTK_WINDOW_LEVEL_ACTION)
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