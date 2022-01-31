import vtk

# Call back function


def sphereCallback(obj, event):
    print('Center: {}, {}, {}'.format(*obj.GetCenter()))


# A renderer and render window
renderer = vtk.vtkRenderer()
renderer.SetBackground(1, 1, 1)

renwin = vtk.vtkRenderWindow()
renwin.AddRenderer(renderer)

# An interactor
interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(renwin)

# A Sphere widget
sphereWidget = vtk.vtkSphereWidget2()
sphereWidget.SetInteractor(interactor)
sphereWidget.CreateDefaultRepresentation()

sphereRepresentation = sphereWidget.GetRepresentation()
sphereRepresentation.HandleVisibilityOn()

# Connect the event to a function
sphereWidget.AddObserver("InteractionEvent", sphereCallback)
sphereWidget.On()
# Start
interactor.Initialize()
interactor.Start()