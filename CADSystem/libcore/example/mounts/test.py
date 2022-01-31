import vtk

"""
Interactor:

Rotate
Pan
Zoom
Toggle
Exit
Quit

"""

reader = vtk.vtkSTLReader()
reader.SetFileName('../../data/rooster.hires.stl')
reader.Update()

shrink = vtk.vtkShrinkPolyData()
shrink.SetInputConnection(reader.GetOutputPort())
shrink.SetShrinkFactor(0.85)
shrink.Update()

polydata = vtk.vtkPolyData()
polydata.ShallowCopy(shrink.GetOutput())

sphere = vtk.vtkSphereSource()
sphere.SetRadius(50.0)
sphere.Update()

sphere_mapper = vtk.vtkPolyDataMapper()
sphere_mapper.SetInputData(sphere.GetOutput())

sphere_actor = vtk.vtkActor()
sphere_actor.SetMapper(sphere_mapper)
sphere_actor.GetProperty().SetColor(0.0, 0.0, 1.0)

mapper = vtk.vtkPolyDataMapper()
mapper.SetInputData(polydata)
actor = vtk.vtkActor()
actor.SetMapper(mapper)

renderer = vtk.vtkRenderer()
renderer.SetBackground(1.0, 0.0, 0.0)
renderer.AddActor(actor)
renderer.AddActor(sphere_actor)


ren_win = vtk.vtkRenderWindow()
ren_win.AddRenderer(renderer)
iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(ren_win)
iren.Initialize()
ren_win.Render()

cam = renderer.GetActiveCamera()
#cam.Azimuth(150)
cam.Elevation(30)

light = vtk.vtkLight()
light.SetColor(1, 1, 0)
light.SetFocalPoint(cam.GetFocalPoint())
light.SetPosition(cam.GetPosition())
renderer.AddLight(light)

sphere_actor.SetPosition(-10, 100, 100)
sphere_actor.SetOrientation(90, 0, 0)
sphere_actor.SetScale(2.0, 1.0, 1.0)

Pick(selection_x, selection_y, selection_z, renderer)

iren.Start()
