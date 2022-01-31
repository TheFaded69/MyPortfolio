"""
https://lorensen.github.io/VTKExamples/site/Cxx/PolyData/MergePoints/
"""

import vtk


# Create a set of points
pointsSource = vtk.vtkPointSource()
pointsSource.SetNumberOfPoints(100)
pointsSource.Update()

points = pointsSource.GetOutput()

# Get a point point in the set
inSet = [0.0, 0.0, 0.0]
points.GetPoint(25, inSet)

print("There are ", points.GetNumberOfPoints(), " input points.")

id = vtk.vtkIdType()

# Insert all of the points
mergePoints = vtk.vtkMergePoints()
mergePoints.SetDataSet(points)
mergePoints.SetDivisions(10,10,10)
mergePoints.InitPointInsertion(points.GetPoints(), points.GetBounds())

for i in range(points.GetNumberOfPoints()):
  mergePoints.InsertUniquePoint(points.GetPoint(i), id)

# Insert a few of the original points
print("Insert some of the original points")

for i in range(points.GetNumberOfPoints()):
  points.GetPoint(i, inSet)
  inserted = mergePoints.InsertUniquePoint(inSet, id)
  std::cout << "\tPoint: "
            << inSet[0] << ", "
            << inSet[1] << ", "
            << inSet[2] << " "

  std::cout << "Inserted? " << ((inserted == 0) ? "No, " : "Yes, ")
  std::cout << "Id:: " << id << std::endl
}

# These points are probably outside the original set of points
std::cout << "Insert some new points" << std::endl
double outsideSet[3]
for (unsigned int i = 0 i < 10 i++)
{
  outsideSet[0] = vtk.vtkMath::Random(
    -pointsSource.GetRadius(),
    pointsSource.GetRadius())
  outsideSet[1] = vtk.vtkMath::Random(
    -pointsSource.GetRadius(),
    pointsSource.GetRadius())
  outsideSet[2] = vtk.vtkMath::Random(
    -pointsSource.GetRadius(),
    pointsSource.GetRadius())

  inserted = mergePoints.InsertUniquePoint(outsideSet, id)
  std::cout << "\tPoint: "
            << outsideSet[0] << ", "
            << outsideSet[1] << ", "
            << outsideSet[2] << " "

  std::cout << "Inserted? " << ((inserted == 0) ? "No, " : "Yes, ")
  std::cout << "Id:: " << id << std::endl
}

std::cout << "There are now "
          << points.GetNumberOfPoints() << " points." << std::endl
