import vtk
from libcore.mixins import ViewportMixin
from libcore.mesh import Mesh
from libcore.display import PolyActor
from libcore.geometry import Plane
from libcore.color import random_color


def make_mesh_with_open_edges():
    mesh = Mesh('../data/rooster.midres.stl')
    mesh.extract_largest(inplace=True)
    cx, cy, cz = mesh.center
    region, _ = mesh.disect_by_plane(Plane(origin=(cx, cy, cz - 40), normal=(0, 0, 1)))
    _, region = region.disect_by_plane(Plane(origin=(cx, cy, cz + 100), normal=(0, 0, 1)))
    return region


def close_mesh(mesh):
    triang = vtk.vtkContourTriangulator()
    triang.SetInputData(mesh.open_edges)
    triang.Update()
    contours = Mesh(triang.GetOutput())
    filled = Mesh.from_meshes([mesh, contours])
    filled.clean(inplace=True)
    return filled


class App(ViewportMixin):

    def __init__(self):
        super().__init__()
        self.style = vtk.vtkInteractorStyleTrackballCamera()
        original = make_mesh_with_open_edges()
        closed = close_mesh(original)

        for edge in original.open_edges.split():
            self.add_prop(PolyActor(edge, representation='surface', edge_visibility=True, render_lines_as_tubes=True, line_width=2.5, color=random_color()))

        self.original_actor = PolyActor(original, color='blue')
        self.add_prop(self.original_actor)

        self.closed_actor = PolyActor(closed, color='red')
        self.closed_actor.hide()
        self.add_prop(self.closed_actor)
        self.register_callback(vtk.vtkCommand.CharEvent, self.event)

        print(closed)


    def event(self, caller, ev):
        key = self.interactor.GetKeySym()
        if key == '1':
            self.original_actor.hide()
            self.closed_actor.show()
        elif key == '2':
            self.original_actor.show()
            self.closed_actor.hide()
        self.rwindow.Render()

app = App()
app.run()
