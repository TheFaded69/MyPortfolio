import vtk

from libcore.mesh import Mesh
from libcore.mixins import ViewportMixin
from libcore.display import PolyActor

class App(ViewportMixin):

    def __init__(self):
        super().__init__()

        original = Mesh('../data/rooster.midres.stl')
        original.compute_normals()
        masked = original.mask_on_ratio(ratio=2)

        self.add_prop(PolyActor(mesh=original, color='green', opacity=0.8))
        self.add_prop(PolyActor(mesh=masked, color='white', opacity=0.2))

if __name__ == '__main__':
    app = App()
    app.run()
