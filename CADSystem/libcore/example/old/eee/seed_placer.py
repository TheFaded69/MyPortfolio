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

        # Create the representation
        self.handle = vtk.vtkPointHandleRepresentation2D()
        self.handle.GetProperty().SetColor(0, 1, 0)
        self.rep = vtk.vtkSeedRepresentation()
        self.rep.SetHandleRepresentation(self.handle)

        # Seed widget
        self.widget = vtk.vtkSeedWidget()
        self.widget.SetInteractor(self.interactor)
        self.widget.SetRepresentation(self.rep)

        self.widget.AddObserver(vtk.vtkCommand.PlacePointEvent, self.callback)
        self.widget.AddObserver(vtk.vtkCommand.InteractionEvent, self.callback)

        self.widget.On()

    def callback(self, caller, event):
        if event == "PlacePointEvent":
            print("Point placed, total of: ", self.rep.GetNumberOfSeeds())
        elif event == "InteractionEvent":
            print("Interacting with seed : ")

        print("List of seeds (Display coordinates):")
        for i in range(self.rep.GetNumberOfSeeds()):
            pos = [0, 0, 0]
            self.rep.GetSeedWorldPosition(i, pos)
            print(pos)


app = App()
app.run()