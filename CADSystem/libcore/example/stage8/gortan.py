import numpy as np
import vtk

import pydicom

from libcore.image import Image
from libcore.mixins import ViewportMixin
from libcore.widget import ImageView
from libcore.display import PolyActor
from libcore.mesh import Mesh
from libcore.dicom import read_metadata, read_volume, load_directory, scan_directory

FILE_NAME = "/home/franz/dicom/perov"




class App(ViewportMixin):

    def __init__(self):
        super().__init__()

        bla = load_directory(FILE_NAME)
        print(bla)

        #
        # self.image = read_wierd_file(filename=FILE_NAME)
        # print(self.image)
        #
        # self.mesh = self.image.extract_surface(discrete=False)
        # print(self.mesh)
        # self.mesh.save('out.stl')
        #
        # self.actor = PolyActor(mesh=self.mesh, opacity=0.5)
        # self.add_prop(self.actor)
        #
        #
        # self.viewer = ImageView(interactor=self.interactor, image=self.image)
        # self.viewer.show()



if __name__ == '__main__':
    app = App()
    app.run()