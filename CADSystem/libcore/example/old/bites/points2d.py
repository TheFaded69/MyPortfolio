import vtk
from libcore.mixins import ViewportMixin
from libcore.color import get_color

class Contour2D(vtk.vtkActor2D):

    def __init__(self, pts, color='white', width=2.0):
        self.mapper = vtk.vtkPolyDataMapper2D()
        self.SetMapper(self.mapper)
        self.set_points(pts)
        self.color = color
        self.width = width

    @property
    def color(self):
        return self.GetProperty().GetColor()

    @color.setter
    def color(self, value):
        self.GetProperty().SetColor(get_color(value))

    @property
    def width(self):
        return self.GetProperty().GetPointSize()

    @width.setter
    def width(self, value):
        self.GetProperty().SetPointSize(value)

    def set_points(self, pts):
        pts = self._pts2polydata(pts)
        self.mapper.SetInputData(pts)

    def _pts2polydata(self, pts):
        points = vtk.vtkPoints()
        for pt in pts:
            print(pt)
            points.InsertNextPoint(pt)

        lines = vtk.vtkCellArray()
        for i in range(len(pts)-1):
            line = vtk.vtkLine()
            line.GetPointIds().SetId(0, i)
            line.GetPointIds().SetId(1, i+1)
            lines.InsertNextCell(line)

        polydata = vtk.vtkPolyData()
        polydata.SetPoints(points)
        polydata.SetLines(lines)
        return polydata


if __name__ == '__main__':
    data = [[0.0, 0.0, 0.0], [100.0, 0.0, 0.0], [0.0, 100.0, 0.0],
            [0.0, 100.0, 2.0], [100.0, 200.0, 300.0], [0.0, 0.0, 0.0]]

    actor = Contour2D(pts=data)
    renderer = vtk.vtkRenderer()
    renderer.SetBackground(0.1, 0.2, 0.3)
    renderer.AddActor(actor)
    renderer.ResetCamera()

    window = vtk.vtkRenderWindow()
    window.AddRenderer(renderer)

    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(window)
    iren.Initialize()

    window.Render()
    iren.Start()