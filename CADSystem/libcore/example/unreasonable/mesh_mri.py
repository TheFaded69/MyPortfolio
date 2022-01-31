import vtk
from libcore.mixins import ViewportMixin
from libcore.display import PolyActor
from libcore.dicom import load_directory

MRI_DIR = '../../data/dicom/mri/'

class App(ViewportMixin):
    def __init__(self):
        super().__init__()
        self.style = vtk.vtkInteractorStyleTrackballCamera()

        self.image = load_directory(MRI_DIR)
        print('MIN: {} MAX: {}'.format(self.image.min_value,
                                       self.image.max_value))

        self.mesh = self.image.extract_surface(threshold=0, threshold2=50)
        self.actor = PolyActor(mesh=self.mesh, color='red')

        self.add_prop(self.actor)


app = App()
app.run()