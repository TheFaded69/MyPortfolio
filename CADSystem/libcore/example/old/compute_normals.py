import vtk

from libcore.mesh import Mesh
from libcore.mixins import ViewportMixin
from libcore.display import PolyActor

class App(ViewportMixin):

    def __init__(self):
        super().__init__()

        original = Mesh('../data/rooster.midres.stl')
        original.compute_normals()
        self.add_prop(PolyActor(mesh=original, color='white'))

if __name__ == '__main__':
    app = App()
    app.run()
