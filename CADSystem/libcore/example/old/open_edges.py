import vtk
from libcore.mixins import ViewportMixin
from libcore.mesh import Mesh
from libcore.display import PolyActor
from libcore.geometry import Plane
from libcore.color import random_color
from libcore.topology import delaunay_surface

def make_mesh_with_open_edges():
    mesh = Mesh('../data/rooster.lowres.stl')
    cx, cy, cz = mesh.center
    region, _ = mesh.disect_by_plane(Plane(origin=(cx, cy, cz - 40), normal=(0, 0, 1)))
    _, region = region.disect_by_plane(Plane(origin=(cx, cy, cz + 100), normal=(0, 0, 1)))
    return region

def rule(mesh):
    #mesh.fill_holes(inplace=True)
    #mesh.triangular(inplace=True)
    rf = vtk.vtkRuledSurfaceFilter()
    rf.SetInputData(mesh)
    rf.SetResolution(30, 30)
    rf.SetRuledModeToResample()
    rf.CloseSurfaceOn()
    
    rf.Update()
    return Mesh(rf.GetOutput())

class App(ViewportMixin):

    def __init__(self):
        super().__init__()
        self.style = vtk.vtkInteractorStyleJoystickCamera()
        mesh = make_mesh_with_open_edges()

        for edge in mesh.open_edges.split():
            self.add_prop(PolyActor(rule(edge), color=random_color()))
            self.add_prop(PolyActor(edge.strip(), line_width=3.5, color=random_color()))

        self.add_prop(PolyActor(mesh, color='blue', opacity=0.5))
        self.renderer.ResetCamera()

app = App()
app.run()
