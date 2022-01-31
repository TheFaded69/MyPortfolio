# Нужно сделать рисование контура "поверх" поверхности
import vtk
import math

import vtk
from libcore.mesh import Mesh
from libcore.display import PolyActor
from libcore.mixins import ViewportMixin



def mkVtkIdList(it):
    vil = vtk.vtkIdList()
    for i in it:
        vil.InsertNextId(int(i))
    return vil

def gen_points():
    points = vtk.vtkPoints()
    lines = vtk.vtkCellArray()

    for i in range(0, 21):
        angle = 2.0 * math.pi * i / 20.0
        points.InsertPoint(i, 0.1 * math.cos(angle), 0.1 * math.sin(angle), 0.0)
    for i in range(0, 20):
        lines.InsertNextCell(mkVtkIdList([i, i+1]))

    pd = vtk.vtkPolyData()
    pd.SetPoints(points)
    pd.SetLines(lines)
    return Mesh(pd)



class App(ViewportMixin):

    def __init__(self):
        super().__init__()

        self.style = vtk.vtkInteractorStyleTrackballCamera()
        self.mesh = Mesh('../data/rooster.midres.stl')
        self.actor = PolyActor(self.mesh)
        self.add_prop(self.actor)

        representation = vtk.vtkOrientedGlyphContourRepresentation()
        representation.GetLinesProperty().SetColor(1, 0, 0)  # set color to red
        self.contour = vtk.vtkContourWidget()
        self.contour.SetInteractor(self.interactor)
        self.contour.SetRepresentation(representation)
        self.contour.On()

        pd = gen_points()
        self.contour.Initialize(pd, 1)
        self.contour.Render()

        self.register_callback(vtk.vtkCommand.CharEvent, self.event)

    def event(self, caller, ev):
        key = self.interactor.GetKeySym()
        if key == '1':
            pass

        self.rwindow.Render()

app = App()
app.run()
