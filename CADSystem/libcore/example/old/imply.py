import vtk
from libcore.mixins import ViewportMixin
from libcore.mesh import Mesh
from libcore.display import PolyActor
from libcore.geometry import Plane
from libcore.color import random_color
from libcore.topology import delaunay_surface


def make_mesh_with_open_edges():
    mesh = Mesh('../../data/rooster.midres.stl')
    mesh.extract_largest(inplace=True)
    cx, cy, cz = mesh.center
    region, _ = mesh.disect_by_plane(Plane(origin=(cx, cy, cz - 40), normal=(0, 0, 1)))
    _, region = region.disect_by_plane(Plane(origin=(cx, cy, cz + 100), normal=(0, 0, 1)))
    return region


class App(ViewportMixin):

    def __init__(self):
        super().__init__()
        self.style = vtk.vtkInteractorStyleJoystickCamera()
        #mesh = make_mesh_with_open_edges()
        mesh = Mesh('../../data/rooster.midres.stl')
        print(mesh.bounds)
        implicit = vtk.vtkImplicitPolyDataDistance()
        implicit.SetInput(mesh)

        box = vtk.vtkBox()
        box.SetBounds(34.604740142822266, 175.79928588867188, 13.59656047821045, 184.78134155273438, 0.07564293593168259, 180.923828125)

        boolean = vtk.vtkImplicitBoolean()
        boolean.SetOperationTypeToIntersection()
        # boolean.SetOperationTypeToUnion()
        # boolean.SetOperationTypeToIntersection()
        boolean.AddFunction(implicit)
        boolean.AddFunction(box)

        sample = vtk.vtkSampleFunction()
        sample.SetImplicitFunction(boolean)
        sample.SetModelBounds(*mesh.bounds)
        sample.SetSampleDimensions(100, 100, 100)
        sample.ComputeNormalsOff()

        # contour
        surface = vtk.vtkContourFilter()
        surface.SetInputConnection(sample.GetOutputPort())
        surface.SetValue(0, 0.0)
        surface.Update()

        result = Mesh(surface.GetOutput())

        self.add_prop(PolyActor(result, color='blue'))
        self.renderer.ResetCamera()

app = App()
app.run()
