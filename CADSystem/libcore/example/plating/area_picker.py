import vtk

def callback(caller, ev):
    props = caller.GetProp3Ds()
    props.InitTraversal()

    for i in range(props.GetNumberOfItems()):
      prop = props.GetNextProp3D()
      print(prop)


# Create a set of points
points = vtk.vtkPoints()
vertices = vtk.vtkCellArray()
pid = [0]
pid[0] = points.InsertNextPoint(1.0, 0.0, 0.0)
vertices.InsertNextCell(1,pid)
pid[0] = points.InsertNextPoint(0.0, 0.0, 0.0)
vertices.InsertNextCell(1, pid)
pid[0] = points.InsertNextPoint(0.0, 1.0, 0.0)
vertices.InsertNextCell(1, pid)

# Create a polydata
polydata = vtk.vtkPolyData()
polydata.SetPoints(points)
polydata.SetVerts(vertices)

# Visualize
mapper = vtk.vtkPolyDataMapper()
mapper.SetInputData(polydata)
colors = vtk.vtkNamedColors()

actor = vtk.vtkActor()
actor.SetMapper(mapper)
actor.GetProperty().SetPointSize(5)
actor.GetProperty().SetColor(colors.GetColor3d("Black"))

renderer = vtk.vtkRenderer()
window = vtk.vtkRenderWindow()
window.AddRenderer(renderer)
area_picker = vtk.vtkAreaPicker()

interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(window)
interactor.SetPicker(area_picker)
renderer.AddActor(actor)
renderer.SetBackground(colors.GetColor3d("Gold"))
window.Render()

style = vtk.vtkInteractorStyleRubberBandPick()
style.SetCurrentRenderer(renderer)
interactor.SetInteractorStyle(style)
area_picker.AddObserver(vtk.vtkCommand.EndPickEvent, callback)
interactor.Start()