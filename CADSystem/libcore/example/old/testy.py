import vtk
from vtk.util.colors import tomato

cylinder = vtk.vtkCylinderSource()
cylinder.SetResolution(8)
cylinder.SetCapping(True)
cylinder.SetHeight(100.0)
cylinder.SetCenter(0, 0, 0)
cylinder.Update()

transform = vtk.vtkTransform()
transform.Identity()
transform.RotateX(50.0)
transform.RotateY(20.0)

cylinder_mapper = vtk.vtkPolyDataMapper()
cylinder_mapper.SetInputData(cylinder.GetOutput())

actor = vtk.vtkActor()
actor.SetMapper(cylinder_mapper)
actor.GetProperty().SetColor(tomato)
actor.SetUserTransform(transform)


ren = vtk.vtkRenderer()

ren_win = vtk.vtkRenderWindow()
ren_win.AddRenderer(ren)
iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(ren_win)
ren.AddActor(actor)
ren.SetBackground(0.1, 0.2, 0.4)
ren_win.SetSize(200, 200)
iren.Initialize()
ren.ResetCamera()
ren.GetActiveCamera().Zoom(1.5)
ren_win.Render()
iren.Start()