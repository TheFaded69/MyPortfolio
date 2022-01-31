import vtk
import math


class Interactor(vtk.vtkInteractorStyle):

    def __init__(self):
        self.MotionFactor = 10.0
        self.InteractionProp = None
        self.InteractionPicker = vtk.vtkCellPicker()
        self.InteractionPicker.SetTolerance(0.001)

    @property
    def interactor(self):
        return self.GetInteractor()

    @property
    def renderer(self):
        return self.interactor.GetRenderWindow().GetRenderers().GetFirstRenderer()

    def OnMouseMove(self):
        x, y = self.interactor.GetEventPosition()

        if self.State == vtk.VTKIS_ROTATE:
            self.FindPokedRenderer(x, y)
            self.Rotate()
            self.InvokeEvent(vtk.vtkCommand.InteractionEvent, None)
        elif self.State == vtk.VTKIS_PAN:
            self.FindPokedRenderer(x, y)
            self.Pan()
            self.InvokeEvent(vtk.vtkCommand.InteractionEvent, None)
        elif self.State == vtk.VTKIS_DOLLY:
            self.FindPokedRenderer(x, y)
            self.Dolly()
            self.InvokeEvent(vtk.vtkCommand.InteractionEvent, None)
        elif self.State == vtk.VTKIS_SPIN:
            self.FindPokedRenderer(x, y)
            self.Spin()
            self.InvokeEvent(vtk.vtkCommand.InteractionEvent, None)
        elif self.State == vtk.VTKIS_USCALE:
            self.FindPokedRenderer(x, y)
            self.UniformScale()
            self.InvokeEvent(vtk.vtkCommand.InteractionEvent, None)

    def OnLeftButtonDown(self):
        x, y = self.interactor.GetEventPosition()

        self.FindPokedRenderer(x, y)
        self.FindPickedActor(x, y)
        if (self.renderer == None) or (self.InteractionProp == None):
            return

        self.GrabFocus(self.EventCallbackCommand)
        if self.interactor.GetShiftKey():
            self.StartPan()
        elif self.interactor.GetControlKey():
            self.StartSpin()
        else:
            self.StartRotate()

    def OnLeftButtonUp(self):
        if self.State == vtk.VTKIS_PAN:
            self.EndPan()
        elif self.State == vtk.VTKIS_SPIN:
            self.EndSpin()
        elif self.State == vtk.VTKIS_ROTATE:
            self.EndRotate()

        if self.interactor:
            self.ReleaseFocus()

    def OnMiddleButtonDown(self):
        x, y = self.interactor.GetEventPosition()

        self.FindPokedRenderer(x, y)
        self.FindPickedActor(x, y)
        if (self.renderer == None) or (self.InteractionProp == None):
            return

        self.GrabFocus(self.EventCallbackCommand)
        if self.interactor.GetControlKey():
            self.StartDolly()
        else:
            self.StartPan()

    def OnMiddleButtonUp(self):
        if self.State == vtk.VTKIS_DOLLY:
            self.EndDolly()
        elif self.State == vtk.VTKIS_PAN:
            self.EndPan()

        if self.interactor:
            self.ReleaseFocus()

    def OnRightButtonDown(self):
        x, y = self.interactor.GetEventPosition()

        self.FindPokedRenderer(x, y)
        self.FindPickedActor(x, y)
        if (self.renderer == None) or (self.InteractionProp == None):
            return

        self.GrabFocus(self.EventCallbackCommand)
        self.StartUniformScale()

    def OnRightButtonUp(self):
        if self.State == vtk.VTKIS_USCALE:
            self.EndUniformScale()
        if self.interactor:
            self.ReleaseFocus()

    def Rotate(self):
        if (self.renderer == None) or (self.InteractionProp == None):
            return

        rwi = self.interactor
        cam = self.renderer.GetActiveCamera()

        # First get the origin of the assembly
        obj_center = self.InteractionProp.GetCenter()

        # GetLength gets the length of the diagonal of the bounding box
        boundRadius = self.InteractionProp.GetLength() * 0.5

        # Get the view up and view right vectors
        view_up = [0.0, 0.0, 0.0]
        view_look = [0.0, 0.0, 0.0]
        view_right = [0.0, 0.0, 0.0]

        cam.OrthogonalizeViewUp()
        cam.ComputeViewPlaneNormal()
        cam.GetViewUp(view_up)
        vtk.vtkMath.Normalize(view_up)
        cam.GetViewPlaneNormal(view_look)
        vtk.vtkMath.Cross(view_up, view_look, view_right)
        vtk.vtkMath.Normalize(view_right)

        # Get the furtherest point from object position+origin
        outsidept = [0, 0, 0]
        outsidept[0] = obj_center[0] + view_right[0] * boundRadius
        outsidept[1] = obj_center[1] + view_right[1] * boundRadius
        outsidept[2] = obj_center[2] + view_right[2] * boundRadius

        # Convert them to display coord
        disp_obj_center = self.ComputeWorldToDisplay(obj_center[0], obj_center[1], obj_center[2])
        outsidept = self.ComputeWorldToDisplay(outsidept[0], outsidept[1], outsidept[2])

        radius = math.sqrt(vtk.vtkMath.Distance2BetweenPoints(disp_obj_center, outsidept))
        nxf = (rwi.GetEventPosition()[0] - disp_obj_center[0]) / radius
        nyf = (rwi.GetEventPosition()[1] - disp_obj_center[1]) / radius
        oxf = (rwi.GetLastEventPosition()[0] - disp_obj_center[0]) / radius
        oyf = (rwi.GetLastEventPosition()[1] - disp_obj_center[1]) / radius

        if (((nxf * nxf + nyf * nyf) <= 1.0) and ((oxf * oxf + oyf * oyf) <= 1.0)):
            newXAngle = vtk.vtkMath.DegreesFromRadians(math.asin(nxf))
            newYAngle = vtk.vtkMath.DegreesFromRadians(math.asin(nyf))
            oldXAngle = vtk.vtkMath.DegreesFromRadians(math.asin(oxf))
            oldYAngle = vtk.vtkMath.DegreesFromRadians(math.asin(oyf))

            scale = [1.0, 1.0, 1.0]

            *rotate = new
            double * [2]

            rotate[0] = new
            double[4]
            rotate[1] = new
            double[4]

            rotate[0][0] = newXAngle - oldXAngle
            rotate[0][1] = view_up[0]
            rotate[0][2] = view_up[1]
            rotate[0][3] = view_up[2]

            rotate[1][0] = oldYAngle - newYAngle
            rotate[1][1] = view_right[0]
            rotate[1][2] = view_right[1]
            rotate[1][3] = view_right[2]

            self.Prop3DTransform(self.InteractionProp, obj_center, 2, rotate, scale)

            if self.AutoAdjustCameraClippingRange:
                self.renderer.ResetCameraClippingRange()
            rwi.Render()

    def Spin(self):
        if (self.renderer == None) or (self.InteractionProp == None):
            return

        rwi = self.interactor
        cam = self.renderer.GetActiveCamera()

        # Get the axis to rotate around = vector from eye to origin
        obj_center = self.InteractionProp.GetCenter()

        motion_vector = [0.0, 0.0, 0.0]
        view_point = [0.0, 0.0, 0.0]

        if cam.GetParallelProjection():
            # If parallel projection, want to get the view plane normal...
            cam.ComputeViewPlaneNormal()
            cam.GetViewPlaneNormal(motion_vector)
        else:
            # Perspective projection, get vector from eye to center of actor
            cam.GetPosition(view_point)
            motion_vector[0] = view_point[0] - obj_center[0]
            motion_vector[1] = view_point[1] - obj_center[1]
            motion_vector[2] = view_point[2] - obj_center[2]
            vtk.vtkMath.Normalize(motion_vector)

        disp_obj_center = [0.0, 0.0, 0.0]
        self.ComputeWorldToDisplay(obj_center[0], obj_center[1], obj_center[2], disp_obj_center)

        newAngle = vtk.vtkMath.DegreesFromRadians(math.atan2(rwi.GetEventPosition()[1] - disp_obj_center[1],
                                                             rwi.GetEventPosition()[0] - disp_obj_center[0]))

        oldAngle = vtk.vtkMath.DegreesFromRadians(math.atan2(rwi.GetLastEventPosition()[1] - disp_obj_center[1],
                                                             rwi.GetLastEventPosition()[0] - disp_obj_center[0]))

        scale[3]
        scale[0] = scale[1] = scale[2] = 1.0

        *rotate = new
        double * [1]
        rotate[0] = new
        double[4]

        rotate[0][0] = newAngle - oldAngle
        rotate[0][1] = motion_vector[0]
        rotate[0][2] = motion_vector[1]
        rotate[0][3] = motion_vector[2]

        self.Prop3DTransform(self.InteractionProp,
                             obj_center,
                             1,
                             rotate,
                             scale)

        if self.AutoAdjustCameraClippingRange:
            self.renderer.ResetCameraClippingRange()

        rwi.Render()

    def Pan(self):
        if (self.renderer == None or self.InteractionProp == None):
            return

        rwi = self.interactor
        # Use initial center as the origin from which to pan

        obj_center = self.InteractionProp.GetCenter()
        disp_obj_center = [0.0, 0.0, 0.0]
        new_pick_point = [0.0, 0.0, 0.0, 0.0]
        old_pick_point = [0.0, 0.0, 0.0, 0.0]
        motion_vector = [0.0, 0.0, 0.0]

        self.ComputeWorldToDisplay(obj_center[0], obj_center[1], obj_center[2],
                                   disp_obj_center)

        self.ComputeDisplayToWorld(rwi.GetEventPosition()[0],
                                   rwi.GetEventPosition()[1],
                                   disp_obj_center[2],
                                   new_pick_point)

        self.ComputeDisplayToWorld(rwi.GetLastEventPosition()[0],
                                   rwi.GetLastEventPosition()[1],
                                   disp_obj_center[2],
                                   old_pick_point)

        motion_vector[0] = new_pick_point[0] - old_pick_point[0]
        motion_vector[1] = new_pick_point[1] - old_pick_point[1]
        motion_vector[2] = new_pick_point[2] - old_pick_point[2]

        if (self.InteractionProp.GetUserMatrix() != None):
            t = vtk.vtkTransform()
            t.PostMultiply()
            t.SetMatrix(self.InteractionProp.GetUserMatrix())
            t.Translate(motion_vector[0], motion_vector[1], motion_vector[2])
            self.InteractionProp.GetUserMatrix().DeepCopy(t.GetMatrix())
            t.Delete()
        else:
            self.InteractionProp.AddPosition(motion_vector[0], motion_vector[1], motion_vector[2])

        if (self.AutoAdjustCameraClippingRange):
            self.renderer.ResetCameraClippingRange()

        rwi.Render()

    def Dolly(self):
        if (self.renderer == None or self.InteractionProp == None):
            return

        rwi = self.interactor
        cam = self.renderer.GetActiveCamera()

        view_point[3], view_focus[3]
        motion_vector[3]

        cam.GetPosition(view_point)
        cam.GetFocalPoint(view_focus)

        center = self.renderer.GetCenter()

        dy = rwi.GetEventPosition()[1] - rwi.GetLastEventPosition()[1]
        yf = dy / center[1] * self.MotionFactor
        dollyFactor = pow(1.1, yf)

        dollyFactor -= 1.0
        motion_vector[0] = (view_point[0] - view_focus[0]) * dollyFactor
        motion_vector[1] = (view_point[1] - view_focus[1]) * dollyFactor
        motion_vector[2] = (view_point[2] - view_focus[2]) * dollyFactor

        if (self.InteractionProp.GetUserMatrix() != None):
            t = vtk.vtkTransform()
            t.PostMultiply()
            t.SetMatrix(self.InteractionProp.GetUserMatrix())
            t.Translate(motion_vector[0], motion_vector[1],
                        motion_vector[2])
            self.InteractionProp.GetUserMatrix().DeepCopy(t.GetMatrix())
            t.Delete()
        else:
            self.InteractionProp.AddPosition(motion_vector)

        if (self.AutoAdjustCameraClippingRange):
            self.renderer.ResetCameraClippingRange()

        rwi.Render()

    def UniformScale(self):
        if (self.renderer == None) or (self.InteractionProp == None):
            return

        rwi = self.interactor

        dy = rwi.GetEventPosition()[1] - rwi.GetLastEventPosition()[1]

        obj_center = self.InteractionProp.GetCenter()
        center = self.renderer.GetCenter()

        yf = dy / center[1] * self.MotionFactor
        scaleFactor = pow(1.1, yf)

        *rotate = None

        scale = [scaleFactor] * 3

        self.Prop3DTransform(self.InteractionProp, obj_center, 0,
                             rotate,
                             scale)

        if (self.AutoAdjustCameraClippingRange):
            self.renderer.ResetCameraClippingRange()
        rwi.Render()

    def FindPickedActor(self, x, y):
        self.InteractionPicker.Pick(x, y, 0.0, self.renderer)
        prop = self.InteractionPicker.GetViewProp()
        if (prop != None):
            self.InteractionProp = vtk.vtkProp3D.SafeDownCast(prop)
        else:
            self.InteractionProp = None

    def Prop3DTransform(prop3D, boxCenter, numRotation, rotate, scale):
        oldMatrix = vtk.vtkMatrix4x4()
        prop3D.GetMatrix(oldMatrix)

        orig = prop3D.GetOrigin()

        newTransform = vtk.vtkTransform()
        newTransform.PostMultiply()
        if (prop3D.GetUserMatrix() != None):
            newTransform.SetMatrix(prop3D.GetUserMatrix())
        else:
            newTransform.SetMatrix(oldMatrix)
        newTransform.Translate(-(boxCenter[0]), -(boxCenter[1]), -(boxCenter[2]))

        for i in range(numRotation):
            newTransform.RotateWXYZ(rotate[i][0], rotate[i][1], rotate[i][2], rotate[i][3])

        if ((scale[0] * scale[1] * scale[2]) != 0.0):
            newTransform.Scale(scale[0], scale[1], scale[2])

        newTransform.Translate(boxCenter[0], boxCenter[1], boxCenter[2])

        # now try to get the composite of translate, rotate, and scale
        newTransform.Translate(-(orig[0]), -(orig[1]), -(orig[2]))
        newTransform.PreMultiply()
        newTransform.Translate(orig[0], orig[1], orig[2])

        if (prop3D.GetUserMatrix() != None):
            newTransform.GetMatrix(prop3D.GetUserMatrix())
        else:
            prop3D.SetPosition(newTransform.GetPosition())
            prop3D.SetScale(newTransform.GetScale())
            prop3D.SetOrientation(newTransform.GetOrientation())

clas