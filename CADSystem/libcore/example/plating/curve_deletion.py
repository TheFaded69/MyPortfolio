import vtk

from libcore import Mesh
from libcore.display import PolyActor
from libcore.interact import StyleDrawPolygon
from libcore.mixins import ViewportMixin

class App(ViewportMixin):

    def __init__(self):
        super().__init__()
        self.mesh = Mesh('../data/111n+.stl')
        self.actor = PolyActor(self.mesh, color='green', edge_visibility=True,
                                              edge_color='black',
                                              line_width=1.0,
                                              opacity=1.0)
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
            self.mesh.extract(res, False, inplace=True)

            if self.actor:
                self.renderer.RemoveActor(self.actor)
            self.mapper = vtk.vtkPolyDataMapper()
            self.mapper.SetInputData(res)
            self.actor = vtk.vtkActor()
            self.actor.SetMapper(self.mapper)
            self.renderer.AddActor(self.actor)
        self.window.Render()


app = App()
app.run()