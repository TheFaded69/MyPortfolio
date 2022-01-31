import vtk

def main():
    colors = vtk.vtkNamedColors()
    disk_source = vtk.vtkDiskSource()

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(disk_source.GetOutputPort())

    actor = vtk.vtkActor()
    actor.GetProperty().SetColor(colors.GetColor3d("Cornsilk"))
    actor.SetMapper(mapper)

    renderer = vtk.vtkRenderer()
    render_window = vtk.vtkRenderWindow()
    render_window.SetWindowName("Disk")
    render_window.AddRenderer(renderer)
    render_window_interactor = vtk.vtkRenderWindowInteractor()