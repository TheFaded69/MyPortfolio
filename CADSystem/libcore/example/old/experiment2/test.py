import vtk

class MouseInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):

    def __init__(self):
        self.AddObserver(vtk.vtkCommand.LeftButtonPressEvent, self.callback)

    def callback(self, caller, event):
        x, y = self.GetInteractor().GetEventPosition()
        self.GetInteractor().GetPicker().Pick(x, y, 0,
                                              self.GetInteractor().GetRenderWindow().GetRenderers().GetFirstRenderer())
        print(self.GetInteractor().GetPicker().GetPickPosition())

sphere = vtk.vtkSphereSource()
sphere.SetCenter(0, 0, 0)
sphere.SetRadius(2.0)
sphere.SetPhiResolution(15)
sphere.SetThetaResolution(15)
sphere.Update()

picker = vtk.vtkWorldPointPicker()

mapper = vtk.vtkPolyDataMapper()
mapper.SetInputData(sphere.GetOutput())
actor = vtk.vtkActor()
actor.SetMapper(mapper)
actor.GetProperty().SetColor(1, 0, 0)

renderer = vtk.vtkRenderer()
renderer.SetBackground(0, 0, 1)
renderer.AddActor(actor)


window = vtk.vtkRenderWindow()
window.AddRenderer(renderer)
interactor = vtk.vtkRenderWindowInteractor()

interactor.SetPicker(picker)
interactor.SetRenderWindow(window)

style = MouseInteractorStyle()
interactor.SetInteractorStyle(style)
interactor.Initialize()
window.Render()
interactor.Start()
