import vtk
import numpy as np

from libcore.mesh import Mesh
from libcore.mixins import ViewportMixin
from libcore.display import PolyActor

def sphere(radius=1.0, center=(0, 0, 0)):
    figure = vtk.vtkSphere()
    figure.SetRadius(1)
    figure.SetCenter(0, 0, 0)
    return figure

def box(bounds=(-1, 1, -1, 1, -1, 1)):
    figure = vtk.vtkBox()
    figure.SetBounds(*bounds)
    return figure

class App(ViewportMixin):

    def __init__(self):
        super().__init__()



if __name__ == '__main__':
    app = App()
    app.run()