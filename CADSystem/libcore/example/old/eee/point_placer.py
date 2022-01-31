import vtk

from libcore.display import PolyActor
from libcore.mesh import Mesh
from libcore.mixins import ViewportMixin

class App(ViewportMixin):

    def __init__(self):
        super().__init__()
        self.mesh = Mesh('../../data/rooster.midres.stl')
        self.actor = PolyActor(self.mesh, color='red')
        self.add_prop(self.actor)

        rep = vtk.vtkPointHandleRepresentation3D()
        rep.SetHandleSize(10)
        rep.SetWorldPosition([0, 0, 0])

        self.widget = vtk.vtkHandleWidget()
        self.widget.SetInteractor(self.interactor)
        self.widget.SetRepresentation(rep)
        self.widget.AddObserver(vtk.vtkCommand.InteractionEvent, self.callback)

        point_placer = vtk.vtkPolygonalSurfacePointPlacer()
        point_placer.AddProp(self.actor)
        point_placer.GetPolys().AddItem(self.mesh)

        #rep.GetLinesProperty().SetColor(1, 0, 0)
        #rep.GetLinesProperty().SetLineWidth(3.0)
        #rep.SetPointPlacer(point_placer)
        rep.ActiveRepresentationOn()
        for d in dir(rep):
            print(d)

        self.widget.EnabledOn()

    def callback(self, caller, event):
        #print(self.widget.GetRepresentation().GetNumberOfNodes())
        pass

app = App()
app.run()