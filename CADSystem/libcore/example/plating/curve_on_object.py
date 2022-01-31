from libcore import Mesh
from libcore.display import PolyActor
from libcore.mixins import ViewportMixin
from libcore.interact import StyleMeshCurveSelection


class App(ViewportMixin):

    def __init__(self):
        super().__init__()
        self.mesh = Mesh('../data/rooster.lowres.stl')
        self.actor = PolyActor(self.mesh)
        self.add_prop(self.actor)
        self.style = StyleMeshCurveSelection()
        self.style.SetDefaultRenderer(self.renderer)
        self.style.set_mesh(self.mesh)

app = App()
app.run()