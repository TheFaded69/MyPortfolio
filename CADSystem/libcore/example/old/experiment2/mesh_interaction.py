import vtk
from libcore.mesh import Mesh
from libcore.display import PolyActor
from libcore.mixins import ViewportMixin
from libcore.topology import delete_cells


def make_dot(point):
    actor = PolyActor(mesh=Mesh.sphere(radius=0.2), color='white')
    actor.SetPosition(point)
    return actor


class App(ViewportMixin):

    def __init__(self):
        super().__init__()
        self.mesh = Mesh.sphere()
        self.actor = PolyActor(mesh=self.mesh, color='red', edge_visibility=True)
        self.dots = list()
        self.picker_actor = vtk.vtkPropPicker()
        self.picker_cell = vtk.vtkCellPicker()
        self.picker_cell.SetTolerance(0.0005)
        self.interactor.SetPicker(self.picker_actor)

        for pt in self.mesh.points:
            self.dots.append(make_dot(pt))
            self.add_prop(self.dots[-1])

        self.selected_actor = None
        self.add_prop(self.actor)

        self.register_callback(vtk.vtkCommand.LeftButtonPressEvent, self.on_left_button_press_event)
        self.register_callback(vtk.vtkCommand.RightButtonPressEvent, self.on_right_button_press_event)

    def on_left_button_press_event(self, caller, event):
        print('on_left_button_press_event')
        # Определяем позицию, где была нажата левая кнопка
        x, y = self.interactor.GetEventPosition()
        # Создаем пикер для выбора актеров
        self.picker_actor.Pick(x, y, 0, self.renderer)
        if self.selected_actor:
            self.selected_actor.color = 'white'

        self.selected_actor = self.picker_actor.GetActor()
        self.selected_actor.color = 'red'

        # Ищем выбранного актера в списке актеров
        idx = self.dots.index(self.selected_actor)
        if idx:
            self.mesh.points[idx] += 1.0
            self.mesh.Modified()

    def on_right_button_press_event(self, caller, event):
        x, y = self.interactor.GetEventPosition()
        self.picker_cell.Pick(x, y, 0, self.renderer)
        cell = self.picker_cell.GetCellId()
        delete_cells(self.mesh, [cell])
        self.renderer.RemoveActor(self.actor)
        self.actor = PolyActor(mesh=self.mesh, color='green')
        self.add_prop(self.actor)

    def run(self):
        self.interactor.Start()

app = App()
app.run()