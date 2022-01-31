import vtk
import math


def point_distance(p0, p1):
    return math.sqrt(vtk.vtkMath.Distance2BetweenPoints(p0, p1))

plane = vtk.vtkPlane()
plane.SetOrigin(0.0, 0.0, 0.0)
plane.SetNormal(1.0, 0.0, 0.0)
point = (0.2, 0.3, 0.4)
print(plane.DistanceToPlane(point))

m = vtk.vtkMatrix4x4()
m.SetElement(0, 0, 1)
m.SetElement(0, 1, 2)
m.SetElement(0, 2, 3)
m.SetElement(0, 3, 4)
m.SetElement(1, 0, 2)
m.SetElement(1, 1, 2)
m.SetElement(1, 2, 3)
m.SetElement(1, 3, 4)
m.SetElement(2, 0, 3)
m.SetElement(2, 1, 2)
m.SetElement(2, 2, 3)
m.SetElement(2, 3, 4)
m.SetElement(3, 0, 4)
m.SetElement(3, 1, 2)
m.SetElement(3, 2, 3)
m.SetElement(3, 3, 4)

pt = vtk.vtkPerspectiveTransform()
pt.SetMatrix(m)

transform = vtk.vtkTransform()
transform.SetMatrix(m)

p = [1.0, 2.0, 3.0]
transform.Tra