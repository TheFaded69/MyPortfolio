import vtk

class LineProbe(object):

    def __init__(self, interactor, prop, on_changed=None):
        self.interactor = interactor
        self.on_changed = on_changed

        self.widget = vtk.vtkLineWidget()
        self.widget.SetInteractor(self.interactor)
        self.widget.SetProp3D(prop)
        self.widget.AddObserver(vtk.vtkCommand.EndInteractionEvent, self.callback)

    def place(self, bounds):
        self.widget.PlaceWidget(bounds)

    def place_at_point(self, pt):
        x, y, z = pt
        self.widget.SetPoint1(x-0.1, y-0.1, z)
        self.widget.SetPoint2(x+0.1, y+0.1, z)

    def as_polydata(self):
        tmp = Mesh()
        self.widget.GetPolyData(tmp)
        return tmp

    def set_on_angle_changed(self, callback):
        self.on_changed = callback

    def callback(self, caller, event):
        spline = vtk.vtkSplineFilter()
        spline.SetInputData(self.as_polydata())
        spline.SetSubdivideToSpecified()
        spline.SetNumberOfSubdivisions(256)
        spline.Update()

        sample_volume = vtk.vtkProbeFilter()
        sample_volume.SetInputData(1, self.image)
        sample_volume.SetInputData(0, spline.GetOutput())
        sample_volume.Update()
        samples = sample_volume.GetOutput().GetPointData().GetArray(0)
        samples = np.array([samples.GetValue(i) for i in range(samples.GetNumberOfValues())])
        if self.on_changed:
            self.on_changed(samples)

    def show(self):
        self.widget.On()

    def hide(self):
        self.widget.Off()


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
