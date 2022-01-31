import math
import vtk

from libcore.mixins import ViewportMixin
from libcore.mesh import Mesh
from libcore.display import PolyActor

def to_implicit(mesh):
    imp = vtk.vtkImplicitPolyDataDistance()
    imp.SetInput(mesh)
    return imp

def implicitly_combine(main, to_add_list, to_subtract_list):
    all_meshes = [main]
    all_meshes.extend(to_add_list)
    all_meshes.extend(to_subtract_list)
    all_mesh = Mesh.from_meshes(all_meshes)
    bounding_box = all_mesh.bounds
    del all_mesh


    main_imp = to_implicit(main)
    to_add_imp = [to_implicit(mesh) for mesh in to_add_list]
    to_subtract_imp = [to_implicit(mesh) for mesh in to_subtract_list]

    boolean_sum = vtk.vtkImplicitBoolean()
    boolean_sum.SetOperationTypeToUnion()
    boolean_sum.AddFunction(main_imp)
    for mesh in to_add_imp:
        boolean_sum.AddFunction(mesh)

    boolean_diff = vtk.vtkImplicitBoolean()
    boolean_diff.SetOperationTypeToDifference()
    boolean_diff.AddFunction(boolean_sum)
    for mesh in to_subtract_imp:
        boolean_diff.AddFunction(mesh)

    sampler = vtk.vtkSampleFunction()
    sampler.SetImplicitFunction(boolean_diff)
    sampler.SetModelBounds(bounding_box)
    sampler.SetSampleDimensions(120, 120, 120)

    surface = vtk.vtkContourFilter()
    surface.SetInputConnection(sampler.GetOutputPort())
    surface.SetValue(0, 0.001)
    surface.Update()

    return Mesh(surface.GetOutput())


class App(ViewportMixin):

    def __init__(self):
        super().__init__()

        self.mesh1 = Mesh('pet_2.stl')
        self.mesh1.fill_holes(hole_size=10, inplace=True)
        self.mesh1.close_mesh(inplace=True)

        self.mesh_add1 = Mesh.cylinder(center=(156, 51, 80), radius=10.0)
        self.mesh_add2 = Mesh.cylinder(center=(116, 51, 80), radius=6.0)

        self.mesh_sub1 = Mesh.cylinder(center=(136, 71, 90), radius=15.0)
        self.mesh_sub2 = Mesh.cylinder(center=(136, 21, 70), radius=10.0)

        self.result_mesh = implicitly_combine(main=self.mesh1,
                                              to_add_list=[self.mesh_add1, self.mesh_add2],
                                              to_subtract_list=[self.mesh_sub1, self.mesh_sub2])

        # self.mesh1 = implicitize(self.mesh1)
        # self.mesh1.fill_holes(hole_size=10, inplace=True)
        # self.mesh1.close_mesh(inplace=True)
        # self.mesh1.extract_largest(inplace=True)

        # self.random_mesh = delaunay_surface(gen_random_pc(num_points=200, radius=1.0))
        self.actor = PolyActor(mesh=self.result_mesh)
        self.add_prop(self.actor)



if __name__ == '__main__':
    app = App()
    app.run()