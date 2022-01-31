import os
import vtk
from libcore import Mesh
from libcore.display import PolyActor
from libcore.mixins import ViewportMixin

def estimate_volume(mesh, simple=True):
    if simple:
        cmp = vtk.vtkMassProperties()
        cmp.SetInputData(mesh)
        cmp.Update()
        return cmp.GetVolume()
    else:
        delaunay = vtk.vtkDelaunay3D()
        delaunay.SetInputData(mesh)
        delaunay.Update()

        surface_filter = vtk.vtkDataSetSurfaceFilter()
        surface_filter.SetInputData(delaunay.GetOutput())
        surface_filter.Update()

        cmp = vtk.vtkMassProperties()
        cmp.SetInputData(surface_filter.GetOutput())
        cmp.Update()
        return cmp.GetVolume()

class App(ViewportMixin):
    def __init__(self):
        super().__init__()
        p = os.path.realpath('../stage8/pet_2.stl')

        self.mesh = Mesh.cube(width=7.0, height=7.2, depth=0.4, tesselation_level=2)
        #self.mesh = Mesh(p)
        self.mesh.move(dx=1.0, dy=0.6, dz=0.75, inplace=True)
        self.mesh.smooth(iterations=10, inplace=True)

        print(estimate_volume(self.mesh, simple=True))

        self.actor = PolyActor(self.mesh,
                                color=(1.0, 1.0, 0.94),
                                edge_visibility=True,
                                edge_color='black',
                                opacity=0.25)

        self.add_prop(self.actor)


app = App()
app.run()