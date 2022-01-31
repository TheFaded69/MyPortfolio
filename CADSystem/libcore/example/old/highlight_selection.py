import vtk

VTKISRBP_ORIENT = 0
VTKISRBP_SELECT = 1

class HighlightInteractorStyle(vtk.vtkInteractorStyleRubberBandPick):

    def __init__(self):
        super().__init__()
        self.PolyData = None
        self.SelectedMapper = vtk.vtkDataSetMapper()
        self.SelectedActor = vtk.vtkActor()
        self.SelectedActor.SetMapper(self.SelectedMapper)
        self.AddObserver(vtk.vtkCommand.LeftButtonReleaseEvent, self.OnLeftButtonUp)

    def SetPolyData(self, polyData):
        self.PolyData = polyData

    def OnLeftButtonUp(self, caller, event):
        super().OnLeftButtonUp()
        print('On left button up!!!')
        frustum = self.GetInteractor().GetPicker().GetFrustum()
        extractPolyDataGeometry = vtk.vtkExtractPolyDataGeometry()
        extractPolyDataGeometry.SetInputData(self.PolyData)
        extractPolyDataGeometry.SetImplicitFunction(frustum)
        extractPolyDataGeometry.Update()

        print("Extracted ", extractPolyDataGeometry.GetOutput().GetNumberOfCells(), " cells.")
        self.SelectedMapper.SetInputData(extractPolyDataGeometry.GetOutput())
        self.SelectedMapper.ScalarVisibilityOff()

        self.SelectedActor.GetProperty().SetColor(1.0, 0.0, 0.0)
        self.SelectedActor.GetProperty().SetPointSize(5)

        self.GetInteractor().GetRenderWindow().GetRenderers().GetFirstRenderer().AddActor(self.SelectedActor)
        self.GetInteractor().GetRenderWindow().Render()
        self.HighlightProp(None)

def main():
    sphereSource = vtk.vtkSphereSource()
    sphereSource.Update()

    idFilter = vtk.vtkIdFilter()
    idFilter.SetInputConnection(sphereSource.GetOutputPort())
    idFilter.SetIdsArrayName("OriginalIds")
    idFilter.Update()

    surfaceFilter = vtk.vtkDataSetSurfaceFilter()
    surfaceFilter.SetInputConnection(idFilter.GetOutputPort())
    surfaceFilter.Update()

    input = surfaceFilter.GetOutput()
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(sphereSource.GetOutputPort())
    mapper.ScalarVisibilityOff()

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetPointSize(5)

    renderer = vtk.vtkRenderer()
    renderWindow = vtk.vtkRenderWindow()
    renderWindow.AddRenderer(renderer)

    areaPicker = vtk.vtkAreaPicker()
    renderWindowInteractor = vtk.vtkRenderWindowInteractor()
    renderWindowInteractor.SetPicker(areaPicker)
    renderWindowInteractor.SetRenderWindow(renderWindow)

    renderer.AddActor(actor)
    renderWindow.Render()

    style = HighlightInteractorStyle()
    for d in dir(style):
        print(d)
    style.SetPolyData(input)
    renderWindowInteractor.SetInteractorStyle(style)
    renderWindowInteractor.Start()

main()