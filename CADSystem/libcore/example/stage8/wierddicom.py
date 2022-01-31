import numpy as np
import vtk

import pydicom

from libcore.image import Image
from libcore.mixins import ViewportMixin
from libcore.widget import ImageView
from libcore.display import PolyActor
from libcore.mesh import Mesh
from libcore.dicom import read_metadata, read_volume

FILE_NAME = "/home/franz/dicom/ashabokova/data/images/Ашабокова ДХ кт 260219.dcm"


def read_wierd_file(filename):
    meta_data = read_metadata(filename)
    ds = pydicom.read_file(filename)
    volume = ds.pixel_array.astype(np.float32)

    spacings = [0.4,
                0.4,
                meta_data['slice_thickness']]

    image = Image.from_numpy(volume, spacing=spacings, origin=(0, 0, 0))
    image.shift_scale(scale=1.0,
                      shift=-1000.0,
                      inplace=True)

    return image


class App(ViewportMixin):

    def __init__(self):
        super().__init__()

        self.image = read_wierd_file(filename=FILE_NAME)
        print(self.image)

        self.mesh = self.image.extract_surface(discrete=False)
        print(self.mesh)
        self.mesh.save('out.stl')

        self.actor = PolyActor(mesh=self.mesh, opacity=0.5)
        self.add_prop(self.actor)


        self.viewer = ImageView(interactor=self.interactor, image=self.image)
        self.viewer.show()



if __name__ == '__main__':
    app = App()
    app.run()