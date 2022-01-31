from libcore import Mesh
from libcore.display import PolyActor
from libcore.interact import StyleRubberBand2D
from libcore.mixins import ViewportMixin


class App(ViewportMixin):

    def __init__(self):
        super().__init__()
        self.mesh = Mesh('../data/rooster.hires.stl')
        self.actor = PolyActor(self.mesh, color='white', edge_visibility=True, opacity=1.0, edge_color='black')
        self.add_prop(self.actor)
        self.style = StyleRubberBand2D()


if __name__ == '__main__':
    app = App()
    app.run()