import vtk

def main():
    inputPolyData = vtk.vtkPolyData()
    sphereSource = vtk.vtkSphereSource()
    sphereSource.SetPhiResolution(15)
    sphereSource.SetThetaResolution(15)
    sphereSource.Update()
    inputPolyData = sphereSource.GetOutput()

    colors = vtk.vtkNamedColors()
    shrink = vtk.vtkShrinkPolyData()
    shrink.SetShrinkFactor(.8)
    shrink.SetInputData(inputPolyData)

    # Visualize
    renderer = vtk.vtkRenderer()
    renderWindow = vtk.vtkRenderWindow()
    renderWindow.AddRenderer(renderer)

    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(renderWindow)
    
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(shrink.GetOutputPort())
    mapper.ScalarVisibilityOff()

    back = vtk.vtkProperty()
    back.SetColor(colors.GetColor3d("Peacock"))

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(colors.GetColor3d("Salmon"))
    actor.SetBackfaceProperty(back)

    renderer.AddActor(actor)
    renderer.SetBackground(colors.GetColor3d("Burlywood"))
    renderer.ResetCamera()
    renderer.GetActiveCamera().Azimuth(30)
    renderer.GetActiveCamera().Elevation(30)
    renderer.GetActiveCamera().Dolly(1.5)
    renderer.ResetCameraClippingRange()

    renderWindow.SetSize(640, 480)
    renderWindow.Render()
    interactor.Start()

main()