import vtk
from libcore.mixins import ViewportMixin
from libcore.color import get_color
from libcore.mesh import Mesh
from libcore.display import PolyActor

def vector_extrude(mesh, nx, ny, nz):
    pass

class App(ViewportMixin):

    def __init__(self):
        super().__init__()
        self.mesh = Mesh('../data/final_brov_duga.stl')
        meshes = list(self.mesh.split())
        self.mesh = meshes[0]
        self.mesh.fill_holes()
        self.mesh.clean()
        self.mesh.reverse_sense()
        self.mesh.subdivide(levels=1, algorithm='linear', inplace=True)

        #self.mesh.smooth(iterations=10, inplace=True)
        # extrude = vtk.vtkLinearExtrusionFilter()
        # extrude.SetInputData(self.mesh)
        # extrude.SetExtrusionTypeToVectorExtrusion()
        # extrude.SetVector(0.707, 0.707, 0.707)
        # extrude.Update()
        # self.mesh = Mesh(extrude.GetOutput())
        # self.mesh.clean()

        #
        # implicit = vtk.vtkImplicitPolyDataDistance()
        # implicit.SetInput(self.mesh)
        #
        # sample = vtk.vtkSampleFunction()
        # sample.SetImplicitFunction(implicit)
        # x0, x1, y0, y1, z0, z1 = self.mesh.bounds
        #
        # sample.SetModelBounds(x0-10, x1+10, y0-10, y1+10, z0-10, z1+10)
        # sample.SetSampleDimensions(120, 120, 120)
        # sample.ComputeNormalsOn()
        # #
        # # # contour
        # surface = vtk.vtkContourFilter()
        # surface.SetInputConnection(sample.GetOutputPort())
        # surface.SetValue(0, 0.5)
        # surface.Update()
        # #
        # self.mesh = Mesh(surface.GetOutput())
        # self.mesh.clean(inplace=True)
        #self.mesh.reverse_sense(inplace=True)
        # #self.mesh.reconstruct_surface(inplace=True)
        #self.mesh.subdivide(levels=1, algorithm='butterfly', inplace=True)
        #self.mesh.smooth(iterations=10, inplace=True)
        self.mesh.save('../data/final_brov_duga_upsample.stl')



        self.actor = PolyActor(self.mesh, color='red')
        self.add_prop(self.actor)

if __name__ == '__main__':
    app = App()
    app.run()
