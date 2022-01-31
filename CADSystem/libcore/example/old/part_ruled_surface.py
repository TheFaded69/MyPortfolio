import vtk

# Create first line.
points = vtk.vtkPoints()
points.InsertPoint(0, 0, 0, 1)
points.InsertPoint(1, 1, 0, 0)
points.InsertPoint(2, 0, 2, 0)
points.InsertPoint(3, 1, 1, 1)

line1 = vtk.vtkLine()
line1.GetPointIds().SetId(0, 0)
line1.GetPointIds().SetId(1, 1)

line2 = vtk.vtkLine()
line2.GetPointIds().SetId(0, 2)
line2.GetPointIds().SetId(1, 3)

lines = vtk.vtkCellArray()
lines.InsertNextCell(line1)
lines.InsertNextCell(line2)

polydata = vtk.vtkPolyData()
polydata.SetPoints(points)
polydata.SetLines(lines)

ruledSurfaceFilter = vtk.vtkRuledSurfaceFilter()
ruledSurfaceFilter.SetInputData(polydata)
ruledSurfaceFilter.SetResolution(21, 21)
ruledSurfaceFilter.SetRuledModeToResample()

renderer = vtk.vtkRenderer()

renderWindow = vtk.vtkRenderWindow()
renderWindow.AddRenderer(renderer)

interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(renderWindow)

mapper = vtk.vtkPolyDataMapper()
mapper.SetInputConnection(ruledSurfaceFilter.GetOutputPort())

actor = vtk.vtkActor()
actor.SetMapper(mapper)
actor.GetProperty().SetColor(0.89, 0.81, 0.34)

# Add the actors to the renderer, set the background and size
renderer.AddActor(actor)
renderer.SetBackground(.3, .4, .5)

renderer.ResetCamera()
renderer.GetActiveCamera().Azimuth(60)
renderer.GetActiveCamera().Elevation(60)
renderer.GetActiveCamera().Dolly(1.2)
renderer.ResetCameraClippingRange()

renderWindow.Render()
interactor.Start()
