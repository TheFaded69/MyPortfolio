import vtk


def gen_sphere_surface():
    sphere_source = vtk.vtkSphereSource()
    sphere_source.SetCenter(0, 0, 0)
    sphere_source.SetPhiResolution(100)
    sphere_source.SetThetaResolution(100)
    sphere_source.SetRadius(1)
    sphere_source.Update()

    sphere_surface = vtk.vtkDataSetSurfaceFilter()
    sphere_surface.SetInputData(sphere_source.GetOutput())
    sphere_surface.Update()
    return sphere_surface.GetOutput()


def cut_surface_by_plane(surface, normal, color, line_width=3):
    plane = vtk.vtkPlane()
    plane.SetOrigin(0, 0, 0)
    plane.SetNormal(normal)

    cutter = vtk.vtkCutter()
    cutter.SetCutFunction(plane)
    cutter.SetInputData(surface)
    cutter.Update()

    cutter_mapper = vtk.vtkDataSetMapper()
    cutter_mapper.SetInputConnection(cutter.GetOutputPort())

    plane_actor = vtk.vtkActor()
    plane_actor.GetProperty().SetColor(color)
    plane_actor.GetProperty().SetLineWidth(line_width)
    plane_actor.GetProperty().RenderLinesAsTubesOn()
    plane_actor.SetMapper(cutter_mapper)

    return plane_actor

def gen_axis():
    sphere = gen_sphere_surface()
    print(sphere)
    # нормаль xz =(1,0,0); XY =(0,0,1), YZ =(0,1,0)
    normals = [(1, 0, 0), (0, 0, 1), (0, 1, 0)]
    colors = [(1, 0, 0), (0, 1, 0), (0, 0, 1)]
    planes = [cut_surface_by_plane(sphere, normal, color) for normal, color in zip(normals, colors)]

    axis = vtk.vtkAssembly()
    for plane in planes:
        axis.AddPart(plane)

    axis.SetOrigin(0, 0, 0)
    return axis


renderer = vtk.vtkRenderer()
render_window = vtk.vtkRenderWindow()
render_window.AddRenderer(renderer)
render_window_interactor = vtk.vtkRenderWindowInteractor()
render_window_interactor.SetRenderWindow(render_window)

renderer.AddActor(gen_axis())

renderer.ResetCamera()
renderer.SetBackground(1, 1, 1)
render_window.Render()
render_window_interactor.Start()