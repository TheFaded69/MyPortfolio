import vtk
from libcore.mixins import ViewportMixin
from libcore.color import get_color
from libcore.mesh import Mesh
from libcore.display import PolyActor

class App(ViewportMixin):

    def __init__(self):
        super().__init__()
        self.mesh = Mesh('../data/76-smooth-min.stl')
        self.mesh.close_mesh(inplace=True)
        self.mesh.fill_holes(inplace=True, hole_size=10000)
        self.mesh.clean(inplace=True)
        self.mesh.reverse_sense(inplace=True)
        #self.mesh.subdivide(levels=2, inplace=True)
        #self.mesh.smooth(iterations=10, inplace=True)
        #self.mesh.reconstruct_surface(inplace=True)
        self.mesh.save('../data/76-smooth-min-closed-cups.stl')

        self.actor = PolyActor(self.mesh, color='red')
        self.add_prop(self.actor)

if __name__ == '__main__':
    app = App()
    app.run()
