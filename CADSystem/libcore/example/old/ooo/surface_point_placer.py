import vtk


class MyCallback(object):

    def __init__(self):
        pass

    def __call__(self, caller, event):
        rep = caller.GetRepresentation()
        print("There are ", rep.GetNumberOfNodes(), " nodes.")

    def SetSphereSource(self, sphere):
        self.SphereSource = sphere


sphereSource = vtk.vtkSphereSource()
sphereSource.SetRadius(5)
sphereSource.Update()

mapper = vtk.vtkPolyDataMapper()
mapper.SetInputConnection(sphereSource.GetOutputPort())

actor = vtk.vtkActor()
actor.SetMapper(mapper)

# Create the RenderWindow, Renderer
renderer = vtk.vtkRenderer()
renderWindow = vtk.vtkRenderWindow()
renderWindow.AddRenderer(renderer)
interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(renderWindow)

renderer.AddActor(actor)

contourWidget = vtk.vtkContourWidget()
contourWidget.SetInteractor(interactor)

callback = MyCallback()
callback.SetSphereSource(sphereSource)
contourWidget.AddObserver(vtk.vtkCommand.InteractionEvent, callback)

rep = contourWidget.GetRepresentation()

pointPlacer = vtk.vtkPolygonalSurfacePointPlacer()
pointPlacer.AddProp(actor)
pointPlacer.GetPolys().AddItem(sphereSource.GetOutput())

rep.GetLinesProperty().SetColor(1, 0, 0)
rep.GetLinesProperty().SetLineWidth(3.0)
rep.SetPointPlacer(pointPlacer)

contourWidget.EnabledOn()
renderer.ResetCamera()
renderWindow.Render()
interactor.Initialize()

interactor.Start()
