import vtk

if __name__ == '__main__':
    point_source = vtk.vtkPointSource()
    point_source.SetNumberOfPoints(50)
    point_source.Update()

    print('There are ')