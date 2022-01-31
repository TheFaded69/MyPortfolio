import vtk

# This does the actual work.
# Callback for the interaction
def callback(caller, event):
    lineWidget = caller
    
    # Get the actual box coordinates of the line
    polydata = vtk.vtkPolyData()
    rep = caller.GetRepresentation()
    rep.GetPolyData(polydata)
    p = [0.0, 0.0, 0.0]
    
    # Display one of the points, just so we know it's working
    polydata.GetPoint(0, p)
    print('P: {} {} {}'.format(p[0], p[1], p[2]))


def main():
  sphereSource = vtk.vtkSphereSource()
  sphereSource.Update()

  # Create a mapper and actor
  mapper = vtk.vtkPolyDataMapper()
  mapper.SetInputConnection(sphereSource.GetOutputPort())
  actor = vtk.vtkActor()
  actor.SetMapper(mapper)

  # A renderer and render window
  renderer = vtk.vtkRenderer()
  renderWindow = vtk.vtkRenderWindow()
  renderWindow.AddRenderer(renderer)

  # An interactor
  renderWindowInteractor = vtk.vtkRenderWindowInteractor()
  renderWindowInteractor.SetRenderWindow(renderWindow)

  lineWidget = vtk.vtkLineWidget2()
  lineWidget.SetInteractor(renderWindowInteractor)
  lineWidget.CreateDefaultRepresentation()


  for d in dir(lineWidget.GetLineRepresentation()):
      print(d)

  # You could do this if you want to set properties at this point:
  lineWidget.AddObserver(vtk.vtkCommand.InteractionEvent, callback)

  # Render
  renderWindow.Render()
  renderWindowInteractor.Initialize()
  renderWindow.Render()
  lineWidget.On()

  # Begin mouse interaction
  renderWindowInteractor.Start()

main()