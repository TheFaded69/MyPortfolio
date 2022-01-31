import vtk

sphereSource = vtk.vtkSphereSource()
sphereSource.Update()

triangleFilter = vtk.vtkTriangleFilter()
triangleFilter.SetInputConnection(sphereSource.GetOutputPort())
triangleFilter.Update()

sphereMapper = vtk.vtkDataSetMapper()
sphereMapper.SetInputConnection(triangleFilter.GetOutputPort())
sphereActor = vtk.vtkActor()
sphereActor.SetMapper(sphereMapper)

mesh = triangleFilter.GetOutput()
print("There are ", mesh.GetNumberOfCells(), " cells.")

qualityFilter = vtk.vtkMeshQuality()

qualityFilter.SetInputData(mesh)
qualityFilter.SetTriangleQualityMeasureToArea()
qualityFilter.Update()

qualityMesh = qualityFilter.GetOutput()
qualityArray = qualityMesh.GetCellData().GetArray("Quality")

print("There are ", qualityArray.GetNumberOfTuples(), " values.")

for i in range(qualityArray.GetNumberOfTuples()):
    val = qualityArray.GetValue(i)
    print("value ", i, " : ", val)

selectCells = vtk.vtkThreshold()
selectCells.ThresholdByLower(.02)
selectCells.SetInputArrayToProcess(0, 0, 0, vtk.vtkDataObject.FIELD_ASSOCIATION_CELLS, vtk.vtkDataSetAttributes.SCALARS)

selectCells.SetInputData(qualityMesh)
selectCells.Update()
ug = selectCells.GetOutput()

# Create a mapper and actor
mapper = vtk.vtkDataSetMapper()
mapper.SetInputData(ug)
actor = vtk.vtkActor()
actor.SetMapper(mapper)
actor.GetProperty().SetColor(1.0, 0.0, 0.0)
actor.GetProperty().SetRepresentationToWireframe()
actor.GetProperty().SetLineWidth(5)

# Create a renderer, render window, and interactor
renderer = vtk.vtkRenderer()
renderWindow = vtk.vtkRenderWindow()
renderWindow.AddRenderer(renderer)
renderWindowInteractor = vtk.vtkRenderWindowInteractor()
renderWindowInteractor.SetRenderWindow(renderWindow)

# Add the actors to the scene
renderer.AddActor(actor)
renderer.AddActor(sphereActor)
renderer.SetBackground(1, 1, 1)  # Background color white

# Render and interact
renderWindow.Render()
renderWindowInteractor.Start()
