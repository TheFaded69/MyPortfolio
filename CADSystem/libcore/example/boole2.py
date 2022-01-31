import vtk

def main():
    colors = vtk.vtkNamedColors()

    sphere = vtk.vtkSphere()
    sphere.SetRadius(1)
    sphere.SetCenter(1, 0, 0)

    box = vtk.vtkBox()
    box.SetBounds(-1, 1, -1, 1, -1, 1)

    hox = vtk.vtkImplicit

    boolean = vtk.vtkImplicitBoolean()
    boolean.SetOperationTypeToDifference()
    boolean.AddFunction(box)
    boolean.AddFunction(sphere)

    sample = vtk.vtkSampleFunction()
    sample.SetImplicitFunction(boolean)
    sample.SetModelBounds(-1, 2, -1, 1, -1, 1)
    sample.SetSampleDimensions(40, 40, 40)
    sample.ComputeNormalsOff()

    surface = vtk.vtkContourFilter()
    surface.SetInputConnection(sample.GetOutputPort())
    surface.SetValue(0, 0.0)

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(surface.GetOutputPort())
    mapper.ScalarVisibilityOff()

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().EdgeVisibilityOn()
    actor.GetProperty().SetColor(colors.GetColor3d("AliceBlue"))
    actor.GetProperty().SetEdgeColor(colors.GetColor3d("SteelBlue"))

    renderer = vtk.vtkRenderer()
    renderer.SetBackground(colors.GetColor3d('Silver'))

    renderer.AddActor(actor)

    renwin = vtk.vtkRenderWindow()
    renwin.AddRenderer(renderer)

    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(renwin)

    interactor.Initialize()
    renwin.Render()
    renderer.GetActiveCamera().SetPosition(5.0, -4.0, 1.6)
    renderer.GetActiveCamera().SetViewUp(0.1, 0.5, 0.9)
    renderer.GetActiveCamera().SetDistance(6.7)
    renwin.Render()
    interactor.Start()

if __name__ == "__main__":
    main()