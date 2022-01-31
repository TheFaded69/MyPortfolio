import vtk

window = vtk.vtkRenderWindow()
renderer = vtk.vtkRenderer()
window.AddRenderer(renderer)
window.Render()

coordinate = vtk.vtkCoordinate()
coordinate.SetCoordinateSystemToDisplay()
coordinate.SetValue(100, 100, 0)
print(coordinate.GetComputedWorldValue(renderer))

# class MouseInteractorStylePP(vtk.vtkInteractorStyleTrackballCamera):
#
#     def __init__(self):
#         super().__init__()
#         self.AddObserver(vtk.vtkCommand.LeftButtonPressEvent, self.OnLeftButtonDown)
#
#     def OnLeftButtonDown(self, caller, event):
#         x, y = self.GetInteractor().GetEventPosition()
#         self.interactor.GetPicker().Pick(x, y, 0, self.renderer)
#         wx, wy, wz = self.interactor.GetPicker().GetPickPosition()
#         print(wx, wy, wz)
#         super().OnLeftButtonDown()
#
#     @property
#     def interactor(self):
#         return self.GetInteractor()
#
#     @property
#     def renderer(self):
#         return self.interactor.GetRenderWindow().GetRenderers().GetFirstRenderer()
#
#
# sphere_source = vtk.vtkSphereSource()
# sphere_source.Update()
#
# picker = vtk.vtkPointPicker()
# mapper = vtk.vtkPolyDataMapper()
# mapper.SetInputConnection(sphere_source.GetOutputPort())
# actor = vtk.vtkActor()
# actor.SetMapper(mapper)
#
# renderer = vtk.vtkRenderer()
# window = vtk.vtkRenderWindow()
# window.AddRenderer(renderer)
# iren = vtk.vtkRenderWindowInteractor()
# iren.SetPicker(picker)
# iren.SetRenderWindow(window)
#
# style = MouseInteractorStylePP()
# iren.SetInteractorStyle(style)
#
# renderer.AddActor(actor)
# renderer.SetBackground(1, 1, 1)
#
# window.Render()
# iren.Start()