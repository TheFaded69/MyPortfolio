import vtk
from libcore import Image
from libcore.display import VolActor
from libcore.mixins import ViewportMixin
from libcore.dicom import load_directory

MRI_DIR = '../../data/dicom/mri/'

class App(ViewportMixin):

    def __init__(self):
        super().__init__()

        self.style = vtk.vtkInteractorStyleTrackballActor()
        self.image = load_directory(MRI_DIR)

        print('Image loaded')

        self.actor = VolActor(self.image, modality='mri', tissue='skin')
        self.add_prop(self.actor)

        self.register_callback(vtk.vtkCommand.CharEvent, self.event)

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

app = App()
app.run()