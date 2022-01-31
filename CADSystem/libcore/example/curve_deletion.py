import vtk

from libcore import Mesh
from libcore.display import PolyActor
from libcore.interact import StyleDrawPolygon
from libcore.mixins import ViewportMixin

class App(ViewportMixin):

    def __init__(self):
        super().__init__()
        self.mesh = Mesh('../data/rooster.midres.stl')
        self.actor = PolyActor(self.mesh, color='blue', edge_visibility=True)
        self.add_prop(self.actor)

        self.style = StyleDrawPolygon()
        self.style.SetDefaultRenderer(self.renderer)
        self.register_callback(vtk.vtkCommand.EndInteractionEvent, self.on_end_interaction)

    def on_end_interaction(self, caller, event):
        if len(self.style.points) > 4:
            contour = self.style.as_polydata()
            nx, ny, nz = self.style.view_vector
            extrude = vtk.vtkLinearExtrusionFilter()
            extrude.SetInputData(contour)
            extrude.SetExtrusionTypeToVectorExtrusion()
            extrude.SetVector(-nx, -ny, -nz)
            extrude.Update()
            res = Mesh(extrude.GetOutput())
            res.fill_holes(inplace=True)

            self.mesh.clip_by_mesh(res, False, inplace=True)

        self.rwindow.Render()


app = App()
app.run()