import vtk
from libcore import Mesh
from libcore.display import PolyActor

class App(object):

    def __init__(self):
        self.renderer = vtk.vtkRenderer()
        self.window = vtk.vtkRenderWindow()
        self.interactor = vtk.vtkRenderWindowInteractor()
        self.window.AddRenderer(self.renderer)
        self.window.SetSize(1024, 800)
        self.interactor.SetRenderWindow(self.window)
        self.interactor.Initialize()

        style = vtk.vtkInteractorStyleTrackballCamera()
        self.interactor.SetInteractorStyle(style)

        self.meshes = [Mesh.sphere(radius=0.5),
                       Mesh.arrow(),
                       Mesh.torus(),
                       Mesh.cube(),
                       Mesh.cone(),
                       Mesh.cylinder(),
                       Mesh.tetrahedra(),
                       Mesh.octahedron(),
                       Mesh.icosahedron(),
                       Mesh.dodecahedron()]

        colors = ['red', 'green', 'white', 'blue', 'yellow', 'orange', 'plum', 'cyan', 'olive', 'violet', 'azure']
        self.actors = []
        for mesh, color in zip(self.meshes, colors):
            print(mesh)
            actor = PolyActor(mesh, color=color, edge_visibility=True, edge_color='black', line_width=1.0, opacity=1.0)
            self.renderer.AddActor(actor)
            self.actors.append(actor)

    def run(self):
        self.interactor.Start()


app = App()
app.run()
