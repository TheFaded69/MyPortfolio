from libcore import Mesh
from libcore.display import PolyActor
from libcore.mixins import ViewportMixin


class App(ViewportMixin):

    def __init__(self):
        super().__init__()
        self.mesh = Mesh.cube(width=7.0, height=1.8, depth=0.4, tesselation_level=2)
        self.mesh.move(dx=1.0, dy=0.6, dz=0.75, inplace=True)
        self.mesh.smooth(iterations=10, inplace=True)

        self.actor = PolyActor(self.mesh,
                                color=(1.0, 1.0, 0.94),
                                edge_visibility=True,
                                edge_color='black',
                                opacity=0.25)

        self.add_prop(self.actor)

app = App()
app.run()