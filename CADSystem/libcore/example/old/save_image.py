import vtk
from libcore.image import Image
from libcore.mixins import ViewportMixin
from libcore.widget import ImageView
import h5py

class App(ViewportMixin):
    def __init__(self):
        super().__init__()
        self.style = vtk.vtkInteractorStyleTrackballCamera()

        self.image = Image()
        self.image.load('../data/rooster.vti')

        fd = h5py.File('../data/roo.hdf5', 'w')
        self.image.save_to_hdf(fd, 'image')
        fd.flush()
        fd.close()

        fd = h5py.File('../data/roo.hdf5', 'r')
        self.image = Image.from_hdf(fd, 'image')

        self.image_view = ImageView(self.interactor, self.image)
        self.image_view.contour_threshold = 200
        self.image_view.show()

app = App()
app.run()