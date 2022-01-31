import vtk


class Callback(object):

    def __init__(self):
        self.Transform = vtk.vtkTransform()

    def __call__(self, caller, event):
        self.AffineRep.GetTransform(self.Transform)
        self.Actor.SetUserTransform(self.Transform)


def main():
    #  Create two spheres: a larger one and a smaller one on top of the larger one
    #  to show a reference point while rotating
    sphere_source = vtk.vtkSphereSource()
    sphere_source.Update()

    sphere_source2 = vtk.vtkSphereSource()
    sphere_source2.SetRadius(0.075)
    sphere_source2.SetCenter(0, 0.5, 0)
    sphere_source2.Update()

    #  Append the two spheres into one vtk.vtkPolyData
    append = vtk.vtkAppendPolyData()
    append.AddInputConnection(sphere_source.GetOutputPort())
    append.AddInputConnection(sphere_source2.GetOutputPort())

    #  Create a plane centered over the larger sphere with 4x4 sub sections
    plane_source = vtk.vtkPlaneSource()
    plane_source.SetXResolution(4)
    plane_source.SetYResolution(4)
    plane_source.SetOrigin(-1, -1, 0)
    plane_source.SetPoint1(1, -1, 0)
    plane_source.SetPoint2(-1, 1, 0)

    #  Create a mapper and actor for the plane: show it as a wireframe
    plane_mapper = vtk.vtkPolyDataMapper()
    plane_mapper.SetInputConnection(plane_source.GetOutputPort())
    plane_actor = vtk.vtkActor()
    plane_actor.SetMapper(plane_mapper)
    plane_actor.GetProperty().SetRepresentationToWireframe()
    plane_actor.GetProperty().SetColor(1, 0, 0)

    #  Create a mapper and actor for the spheres
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(append.GetOutputPort())
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    #  Create a renderer and render window
    renderer = vtk.vtkRenderer()
    render_window = vtk.vtkRenderWindow()
    render_window.AddRenderer(renderer)
    renderer.AddActor(actor)
    renderer.AddActor(plane_actor)
    renderer.GradientBackgroundOn()
    renderer.SetBackground(1, 1, 1)
    renderer.SetBackground2(0, 0, 1)

    #  Create an interactor
    render_window_interactor = vtk.vtkRenderWindowInteractor()
    render_window_interactor.SetRenderWindow(render_window)
    render_window_interactor.GetInteractorStyle().SetCurrentStyleToTrackballCamera()

    #  Create an affine widget to manipulate the actor
    #  the widget currently only has a 2D representation and therefore applies transforms in the X-Y plane only
    affine_widget = vtk.vtkAffineWidget()
    affine_widget.SetInteractor(render_window_interactor)
    affine_widget.CreateDefaultRepresentation()
    repr = affine_widget.GetRepresentation()
    repr.PlaceWidget(actor.GetBounds())
    repr.PickableOn()
    #repr.PickingManagedOn()
    repr.SetAxesWidth(2)
    repr.SetCircleWidth(3)
    repr.SetDragable(False)
    repr.SetHandleSize(3)
    repr.GetProperty().SetColor(1, 0, 0)
    repr.GetSelectedProperty().SetColor(0, 1, 0)


    for d in dir(affine_widget.GetRepresentation()):
        print(d)

    affine_callback = Callback()
    affine_callback.Actor = actor
    affine_callback.AffineRep = affine_widget.GetRepresentation()

    affine_widget.AddObserver(vtk.vtkCommand.InteractionEvent, affine_callback)
    affine_widget.AddObserver(vtk.vtkCommand.EndInteractionEvent, affine_callback)

    render_window.Render()
    render_window_interactor.Initialize()
    render_window.Render()
    affine_widget.On()

    #  begin mouse interaction
    render_window_interactor.Start()


main()
