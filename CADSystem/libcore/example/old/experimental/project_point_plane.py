import vtk

sequence = vtk.vtkMinimalStandardRandomSequence

p = [23.1, 54.6, 9.2]
origin = [0.0, 0.0, 0.0]
normal = [0.0, 0.0, 1.0]
projected = [0.0, 0.0, 0.0]

plane.ProjectPoint(p, origin, normal, projected)
print(projected[0], projected[1], projected[2])