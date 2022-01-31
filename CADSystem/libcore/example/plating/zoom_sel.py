from libcore import Mesh
from libcore.display import PolyActor
from libcore.interact import StyleRubberBandZoom
from libcore.mixins import ViewportMixin
import vtk

class App(ViewportMixin):

    def __init__(self):
        super().__init__()
        self.mesh = Mesh('../data/rooster.hires.stl')
        self.actor = PolyActor(self.mesh, color='white', edge_visibility=True, opacity=1.0, edge_color='black')
        self.add_prop(self.actor)
        self.style = StyleRubberBandZoom()
        #for d in dir(self.style):
        #    print(d)

    def user(self):
        frustum = self.rectum.frustum()
        self.mesh.extract(frustum, inverse=self.button.state(), inplace=True)
        self.window.Render()

if __name__ == '__main__':
    app = App()
    app.run()