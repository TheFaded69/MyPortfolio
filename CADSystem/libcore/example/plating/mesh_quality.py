import vtk

sphereSource = vtk.vtkSphereSource()
sphereSource.Update()

triangleFilter = vtk.vtkTriangleFilter()
triangleFilter.SetInputConnection(sphereSource.GetOutputPort())
triangleFilter.Update()

mesh = triangleFilter.GetOutput()
print("There are ", mesh.GetNumberOfCells(), " cells.")
qualityFilter = vtk.vtkMeshQuality()
qualityFilter.SetInputData(mesh)
qualityFilter.SetTriangleQualityMeasureToArea()
qualityFilter.Update()

qualityArray = qualityFilter.GetOutput().GetCellData().GetArray("Quality")

print("There are ", qualityArray.GetNumberOfTuples(), " values.")

for i in range(qualityArray.GetNumberOfTuples()):
    val = qualityArray.GetValue(i)
    print("value ", i, " : ", val)

polydata = vtk.vtkPolyData()
polydata.ShallowCopy(qualityFilter.GetOutput())

# Visualize
mapper = vtk.vtkPolyDataMapper()
mapper.SetInputData(polydata)
mapper.SetScalarRange(polydata.GetScalarRange())

actor = vtk.vtkActor()
actor.SetMapper(mapper)

renderer = vtk.vtkRenderer()
renderWindow = vtk.vtkRenderWindow()
renderWindow.AddRenderer(renderer)
renderWindowInteractor = vtk.vtkRenderWindowInteractor()
renderWindowInteractor.SetRenderWindow(renderWindow)

renderer.AddActor(actor)
renderer.SetBackground(.3, .6, .3)
renderWindow.Render()
renderWindowInteractor.Start()
