import vtk

class MyInteractor(vtk.vtkInteractorStyleTrackballCamera):

    def __init__(self):
        self.VisibleFilter = None
        self.AddObserver(vtk.vtkCommand.LeftButtonPressEvent, self.OnLeftButtonDown)

    def OnLeftButtonDown(self, caller, event):
        if self.VisibleFilter:
            self.VisibleFilter.Update()
            print("There are currently: ",
                  self.VisibleFilter.GetOutput().GetNumberOfPoints(),
                  " visible.")
        super().OnLeftButtonDown()

    def SetVisibleFilter(self, vis):
        self.VisibleFilter = vis

def main():
    # Создаем меш сферы
    sphere_source = vtk.vtkSphereSource()
    sphere_source.SetCenter(5.0, 0, 0)
    sphere_source.Update()

    # Набор точек
    point_source = vtk.vtkPointSource()
    point_source.SetRadius(2.0)
    point_source.SetNumberOfPoints(200)
    point_source.Update()

    # Создаем актер и маппер
    sphere_mapper = vtk.vtkPolyDataMapper()
    sphere_mapper.SetInputConnection(sphere_source.GetOutputPort())
    sphere_actor = vtk.vtkActor()
    sphere_actor.SetMapper(sphere_mapper)
    points_mapper = vtk.vtkPolyDataMapper()
    points_mapper.SetInputConnection(point_source.GetOutputPort())

    points_actor = vtk.vtkActor()
    points_actor.SetMapper(points_mapper)

    # Создать renderer, окно рендеринга, интерактор
    renderer = vtk.vtkRenderer()
    render_window = vtk.vtkRenderWindow()
    render_window.AddRenderer(renderer)
    render_window_interactor = vtk.vtkRenderWindowInteractor()
    render_window_interactor.SetRenderWindow(render_window)

    # Добавляем актеров на сцену
    renderer.AddActor(sphere_actor)
    renderer.AddActor(points_actor)

    select_visible_points = vtk.vtkSelectVisiblePoints()
    select_visible_points.SetInputConnection(point_source.GetOutputPort())
    select_visible_points.SetRenderer(renderer)
    select_visible_points.Update()

    style = MyInteractor()
    render_window_interactor.SetInteractorStyle(style)
    style.SetVisibleFilter(select_visible_points)

    render_window.Render()
    render_window_interactor.Start()

main()