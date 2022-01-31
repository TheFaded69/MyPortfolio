import math
import vtk

VTK_SPHERE_OFF = 0
VTK_SPHERE_WIREFRAME = 1
VTK_SPHERE_SURFACE = 2


class SphereWidget(vtk.vtk3DWidget):
    Start = 0
    Moving = 1
    Scaling = 2
    Positioning = 3
    Outside = 4

    def __init__(self):
        self.State = SphereWidget.Start
        self.EventCallbackCommand.SetCallback(SphereWidget.ProcessEvents)

        self.Representation = VTK_SPHERE_WIREFRAME

        # Build the representation of the widget
        #  Represent the sphere
        self.SphereSource = vtk.vtkSphereSource()
        self.SphereSource.SetThetaResolution(16)
        self.SphereSource.SetPhiResolution(8)
        self.SphereSource.LatLongTessellationOn()
        self.SphereMapper = vtk.vtkPolyDataMapper()
        self.SphereMapper.SetInputConnection(self.SphereSource.GetOutputPort())
        self.SphereActor = vtk.vtkActor()
        self.SphereActor.SetMapper(self.SphereMapper)

        #  controls
        self.Translation = 1
        self.Scale = 1

        #  handles
        self.HandleVisibility = 0
        self.HandleDirection[0] = 1.0
        self.HandleDirection[1] = 0.0
        self.HandleDirection[2] = 0.0
        self.HandleSource = vtk.vtkSphereSource()
        self.HandleSource.SetThetaResolution(16)
        self.HandleSource.SetPhiResolution(8)
        self.HandleMapper = vtk.vtkPolyDataMapper()
        self.HandleMapper.SetInputConnection(
            self.HandleSource.GetOutputPort())
        self.HandleActor = vtk.vtkActor()
        self.HandleActor.SetMapper(self.HandleMapper)

        #  Define the point coordinates
        bounds = [0.0] * 6
        bounds[0] = -0.5
        bounds[1] = 0.5
        bounds[2] = -0.5
        bounds[3] = 0.5
        bounds[4] = -0.5
        bounds[5] = 0.5

        #  Initial creation of the widget, serves to initialize it
        self.PlaceWidget(bounds)

        # Manage the picking stuff
        self.Picker = vtk.vtkCellPicker()
        self.Picker.SetTolerance(0.005)  # need some fluff
        self.Picker.AddPickList(self.SphereActor)
        self.Picker.AddPickList(self.HandleActor)
        self.Picker.PickFromListOn()

        #  Set up the initial properties
        self.SphereProperty = None
        self.SelectedSphereProperty = None
        self.HandleProperty = None
        self.SelectedHandleProperty = None
        self.CreateDefaultProperties()

    def SetRepresentationToOff(self):
        self.SetRepresentation(VTK_SPHERE_OFF)

    def SetRepresentationToWireframe(self):
        self.SetRepresentation(VTK_SPHERE_WIREFRAME)

    def SetRepresentationToSurface(self):
        self.SetRepresentation(VTK_SPHERE_SURFACE)

    def SetThetaResolution(self, r):
        self.SphereSource.SetThetaResolution(r)

    def GetThetaResolution(self):
        return self.SphereSource.GetThetaResolution()

    def SetPhiResolution(self, r):
        self.SphereSource.SetPhiResolution(r)

    def GetPhiResolution(self):
        return self.SphereSource.GetPhiResolution()

    def SetRadius(self, r):
        if r <= 0:
            r = .00001
        self.SphereSource.SetRadius(r)

    def GetRadius(self):
        return self.SphereSource.GetRadius()

    def SetCenter(self, x, y, z):
        self.SphereSource.SetCenter(x, y, z)

    def SetCenter(self, x):
        self.SetCenter(x[0], x[1], x[2])

    def GetCenter(self):
        return self.SphereSource.GetCenter()

    def GetCenter(self, xyz):
        self.SphereSource.GetCenter(xyz)

    def SetEnabled(self, enabling):
        if not self.Interactor:
            print("The interactor must be set prior to enabling/disabling widget")
            return

        if enabling:  # ----------------------------------------------------------
            print("Enabling sphere widget")

            if self.Enabled:  # already enabled, just return
                return

            if not self.CurrentRenderer:
                self.SetCurrentRenderer(
                    self.Interactor.FindPokedRenderer(
                        self.Interactor.GetLastEventPosition()[0],
                        self.Interactor.GetLastEventPosition()[1]))
                if self.CurrentRenderer == None:
                    return

            self.Enabled = 1

            #  listen for the following events
            i = self.Interactor
            i.AddObserver(vtk.vtkCommand.MouseMoveEvent,
                          self.EventCallbackCommand, self.Priority)
            i.AddObserver(vtk.vtkCommand.LeftButtonPressEvent,
                          self.EventCallbackCommand, self.Priority)
            i.AddObserver(vtk.vtkCommand.LeftButtonReleaseEvent,
                          self.EventCallbackCommand, self.Priority)
            i.AddObserver(vtk.vtkCommand.RightButtonPressEvent,
                          self.EventCallbackCommand, self.Priority)
            i.AddObserver(vtk.vtkCommand.RightButtonReleaseEvent,
                          self.EventCallbackCommand, self.Priority)

            #  Add the sphere
            self.CurrentRenderer.AddActor(self.SphereActor)
            self.SphereActor.SetProperty(self.SphereProperty)

            self.CurrentRenderer.AddActor(self.HandleActor)
            self.HandleActor.SetProperty(self.HandleProperty)
            self.SelectRepresentation()
            self.SizeHandles()
            self.RegisterPickers()

            self.InvokeEvent(vtk.vtkCommand.EnableEvent, None)
        else:  # disabling----------------------------------------------------------
            print("Disabling sphere widget")

            if not self.Enabled:  # already disabled, just return
                return

            self.Enabled = 0

            #  don't listen for events any more
            self.Interactor.RemoveObserver(self.EventCallbackCommand)

            #  turn off the sphere
            self.CurrentRenderer.RemoveActor(self.SphereActor)
            self.CurrentRenderer.RemoveActor(self.HandleActor)

            self.InvokeEvent(vtk.vtkCommand.DisableEvent, None)
            self.SetCurrentRenderer(None)
            self.UnRegisterPickers()

        self.Interactor.Render()

    def ProcessEvents(self, caller, event):
        # okay, let's do the right thing
        if event == "LeftButtonPressEvent":
            self.OnLeftButtonDown()
        elif event == "LeftButtonReleaseEvent":
            self.OnLeftButtonUp()
        elif event == "RightButtonPressEvent":
            self.OnRightButtonDown()
        elif event == "RightButtonReleaseEvent":
            self.OnRightButtonUp()
        elif event == "MouseMoveEvent":
            self.OnMouseMove()

    def SelectRepresentation(self):
        if not self.HandleVisibility:
            self.CurrentRenderer.RemoveActor(self.HandleActor)

        if self.Representation == VTK_SPHERE_OFF:
            self.CurrentRenderer.RemoveActor(self.SphereActor)
        elif self.Representation == VTK_SPHERE_WIREFRAME:
            self.CurrentRenderer.RemoveActor(self.SphereActor)
            self.CurrentRenderer.AddActor(self.SphereActor)
            self.SphereProperty.SetRepresentationToWireframe()
            self.SelectedSphereProperty.SetRepresentationToWireframe()
        else:  # if ( self.Representation == VTKSPHERE_SURFACE )
            self.CurrentRenderer.RemoveActor(self.SphereActor)
            self.CurrentRenderer.AddActor(self.SphereActor)
            self.SphereProperty.SetRepresentationToSurface()
            self.SelectedSphereProperty.SetRepresentationToSurface()

    def GetSphere(self, sphere):
        sphere.SetRadius(self.SphereSource.GetRadius())
        sphere.SetCenter(self.SphereSource.GetCenter())

    def HighlightSphere(self, highlight):
        if highlight:
            self.ValidPick = 1
            self.Picker.GetPickPosition(self.LastPickPosition)
            self.SphereActor.SetProperty(self.SelectedSphereProperty)
        else:
            self.SphereActor.SetProperty(self.SphereProperty)

    def HighlightHandle(self, highlight):
        if highlight:
            self.ValidPick = 1
            self.Picker.GetPickPosition(self.LastPickPosition)
            self.HandleActor.SetProperty(self.SelectedHandleProperty)
        else:
            self.HandleActor.SetProperty(self.HandleProperty)

    def OnLeftButtonDown(self):
        if not self.Interactor:
            return

        X, Y = self.Interactor.GetEventPosition()

        #  Okay, make sure that the pick is in the current renderer
        if (not self.CurrentRenderer) or (not self.CurrentRenderer.IsInViewport(X, Y)):
            self.State = SphereWidget.Outside
            return

        #  Okay, we can process self. Try to pick handles first
        #  if no handles picked, then try to pick the sphere.
        path = self.GetAssemblyPath(X, Y, 0., self.Picker)

        if path == None:
            self.State = SphereWidget.Outside
            return
        elif path.GetFirstNode().GetViewProp() == self.SphereActor:
            self.State = SphereWidget.Moving
            self.HighlightSphere(1)
        elif path.GetFirstNode().GetViewProp() == self.HandleActor:
            self.State = SphereWidget.Positioning
            self.HighlightHandle(1)

        self.EventCallbackCommand.SetAbortFlag(1)
        self.StartInteraction()
        self.InvokeEvent(vtk.vtkCommand.StartInteractionEvent, None)
        self.Interactor.Render()

    # ----------------------------------------------------------------------------
    def OnMouseMove(self):
        #  See whether we're active
        if (self.State == SphereWidget.Outside) or (self.State == SphereWidget.Start):
            return

        if not self.Interactor:
            return

        X, Y = self.Interactor.GetEventPosition()

        #  Do different things depending on state
        #  Calculations everybody does
        focalPoint = [0.0] * 4
        pickPoint = [0.0] * 4
        prevPickPoint = [0.0] * 4
        z = 0.0

        camera = self.CurrentRenderer.GetActiveCamera()
        if not camera:
            return

        #  Compute the two points defining the motion vector
        camera.GetFocalPoint(focalPoint)
        self.ComputeWorldToDisplay(focalPoint[0], focalPoint[1], focalPoint[2], focalPoint)
        z = focalPoint[2]
        self.ComputeDisplayToWorld(float(self.Interactor.GetLastEventPosition()[0]),
                                   float(self.Interactor.GetLastEventPosition()[1]),
                                   z,
                                   prevPickPoint)
        self.ComputeDisplayToWorld(float(X), float(Y), z, pickPoint)

        #  Process the motion
        if self.State == SphereWidget.Moving:
            self.Translate(prevPickPoint, pickPoint)
        elif self.State == SphereWidget.Scaling:
            self.ScaleSphere(prevPickPoint, pickPoint, X, Y)
        elif self.State == SphereWidget.Positioning:
            self.MoveHandle(prevPickPoint, pickPoint, X, Y)

        #  Interact, if desired
        self.EventCallbackCommand.SetAbortFlag(1)
        self.InvokeEvent(vtk.vtkCommand.InteractionEvent, None)
        self.Interactor.Render()

    def OnLeftButtonUp(self):
        if self.State == SphereWidget.Outside:
            return

        self.State = SphereWidget.Start
        self.HighlightSphere(0)
        self.HighlightHandle(0)
        self.SizeHandles()

        self.EventCallbackCommand.SetAbortFlag(1)
        self.EndInteraction()
        self.InvokeEvent(vtk.vtkCommand.EndInteractionEvent, None)
        if self.Interactor:
            self.Interactor.Render()

    def OnRightButtonDown(self):
        if not self.Interactor:
            return

        self.State = SphereWidget.Scaling

        X, Y = self.Interactor.GetEventPosition()

        #  Okay, make sure that the pick is in the current renderer
        if (not self.CurrentRenderer) or (not self.CurrentRenderer.IsInViewport(X, Y)):
            self.State = SphereWidget.Outside
            return
        #  Okay, we can process self. Try to pick handles first
        #  if no handles picked, then pick the bounding box.
        path = self.GetAssemblyPath(X, Y, 0., self.Picker)

        if path == None:
            self.State = SphereWidget.Outside
            self.HighlightSphere(0)
            return
        else:
            self.HighlightSphere(1)

        self.EventCallbackCommand.SetAbortFlag(1)
        self.StartInteraction()
        self.InvokeEvent(vtk.vtkCommand.StartInteractionEvent, None)
        self.Interactor.Render()

    def OnRightButtonUp(self):
        if self.State == SphereWidget.Outside:
            return

        self.State = SphereWidget.Start
        self.HighlightSphere(0)
        self.HighlightHandle(0)
        self.SizeHandles()

        self.EventCallbackCommand.SetAbortFlag(1)
        self.EndInteraction()
        self.InvokeEvent(vtk.vtkCommand.EndInteractionEvent, None)
        if self.Interactor:
            self.Interactor.Render()

    def Translate(self, p1, p2):
        if not self.Translation:
            return

        # Get the motion vector
        v = [0.0] * 3
        v[0] = p2[0] - p1[0]
        v[1] = p2[1] - p1[1]
        v[2] = p2[2] - p1[2]

        # int res = self.SphereSource.GetResolution()
        center = self.SphereSource.GetCenter()

        center1 = [0.0] * 3
        for i in range(3):
            center1[i] = center[i] + v[i]
            self.HandlePosition[i] += v[i]

        self.SphereSource.SetCenter(center1)
        self.HandleSource.SetCenter(self.HandlePosition)
        self.SelectRepresentation()

    # ----------------------------------------------------------------------------
    def ScaleSphere(self, p1, p2, X=0, Y=0):
        if not self.Scale:
            return

        # Get the motion vector
        v = [0.0] * 3
        v[0] = p2[0] - p1[0]
        v[1] = p2[1] - p1[1]
        v[2] = p2[2] - p1[2]

        radius = self.SphereSource.GetRadius()
        c = self.SphereSource.GetCenter()

        #  Compute the scale factor
        sf = 0.0
        if radius > 0.0:
            sf = vtk.vtkMath.Norm(v) / radius
            if Y > self.Interactor.GetLastEventPosition()[1]:
                sf = 1.0 + sf
            else:
                sf = 1.0 - sf
            radius *= sf
        else:
            radius = vtk.VTK_DBL_EPSILON

        self.SphereSource.SetRadius(radius)
        self.HandlePosition[0] = c[0] + sf * (self.HandlePosition[0] - c[0])
        self.HandlePosition[1] = c[1] + sf * (self.HandlePosition[1] - c[1])
        self.HandlePosition[2] = c[2] + sf * (self.HandlePosition[2] - c[2])
        self.HandleSource.SetCenter(self.HandlePosition)

        self.SelectRepresentation()

    def MoveHandle(self, p1, p2, X=0, Y=0):
        # Get the motion vector
        v = [0.0] * 3
        v[0] = p2[0] - p1[0]
        v[1] = p2[1] - p1[1]
        v[2] = p2[2] - p1[2]

        #  Compute the new location of the sphere
        center = self.SphereSource.GetCenter()
        radius = self.SphereSource.GetRadius()

        #  set the position of the sphere
        p = [0.0] * 3
        for i in range(3):
            p[i] = self.HandlePosition[i] + v[i]
            self.HandleDirection[i] = p[i] - center[i]

        self.PlaceHandle(center, radius)
        self.SelectRepresentation()

    def CreateDefaultProperties(self):
        if not self.SphereProperty:
            self.SphereProperty = vtk.vtkProperty()

        if not self.SelectedSphereProperty:
            self.SelectedSphereProperty = vtk.vtkProperty()

        if not self.HandleProperty:
            self.HandleProperty = vtk.vtkProperty()
            self.HandleProperty.SetColor(1, 1, 1)

        if not self.SelectedHandleProperty:
            self.SelectedHandleProperty = vtk.vtkProperty()
            self.SelectedHandleProperty.SetColor(1, 0, 0)

    def PlaceWidget(self, bds):
        bounds = [0.0] * 6
        center = [0.0] * 3
        radius = 0.0

        self.AdjustBounds(bds, bounds, center)

        radius = (bounds[1] - bounds[0]) / 2.0
        if radius > ((bounds[3] - bounds[2]) / 2.0):
            radius = (bounds[3] - bounds[2]) / 2.0

        radius = (bounds[1] - bounds[0]) / 2.0
        if radius > ((bounds[5] - bounds[4]) / 2.0):
            radius = (bounds[5] - bounds[4]) / 2.0

        self.SphereSource.SetCenter(center)
        self.SphereSource.SetRadius(radius)
        self.SphereSource.Update()

        #  place the handle
        self.PlaceHandle(center, radius)

        for i in range(6):
            self.InitialBounds[i] = bounds[i]

        self.InitialLength = math.sqrt((bounds[1] - bounds[0]) * (bounds[1] - bounds[0]) +
                                       (bounds[3] - bounds[2]) * (bounds[3] - bounds[2]) +
                                       (bounds[5] - bounds[4]) * (bounds[5] - bounds[4]))

        self.SizeHandles()

    def PlaceHandle(self, center, radius):
        sf = radius / vtk.vtkMath.Norm(self.HandleDirection)
        self.HandlePosition[0] = center[0] + sf * self.HandleDirection[0]
        self.HandlePosition[1] = center[1] + sf * self.HandleDirection[1]
        self.HandlePosition[2] = center[2] + sf * self.HandleDirection[2]
        self.HandleSource.SetCenter(self.HandlePosition)

    def SizeHandles(self):
        radius = self.vtk.vtk3DWidget.SizeHandles(1.25)
        self.HandleSource.SetRadius(radius)

    def RegisterPickers(self):
        pm = self.GetPickingManager()
        if not pm:
            return
        pm.AddPicker(self.Picker, self)

    def GetPolyData(self, pd):
        pd.ShallowCopy(self.SphereSource.GetOutput())


def sphereCallback(obj, event):
    print('Center: {}, {}, {}'.format(*obj.GetCenter()))


if __name__ == '__main__':
    # A renderer and render window
    renderer = vtk.vtkRenderer()
    renderer.SetBackground(1, 1, 1)

    renwin = vtk.vtkRenderWindow()
    renwin.AddRenderer(renderer)

    # An interactor
    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(renwin)

    # A Sphere widget
    sphereWidget = SphereWidget()
    sphereWidget.SetInteractor(interactor)
    sphereWidget.SetRepresentationToSurface()
    sphereWidget.On()

    # Connect the event to a function
    sphereWidget.AddObserver("InteractionEvent", sphereCallback)

    # Start
    interactor.Initialize()
    interactor.Start()
