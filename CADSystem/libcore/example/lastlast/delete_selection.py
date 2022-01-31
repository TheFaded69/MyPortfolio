# Удаление части меша, выделенной по поверхности
import vtk

from libcore.mixins import ViewportMixin
from libcore.display import PolyActor
from libcore.mesh import Mesh
from libcore.interact import CircleSelection
from libcore.topology import delete_cells
from libcore.topology import face_for_point

class App(ViewportMixin):

    def __init__(self):
        super().__init__()
        self.mesh = Mesh('../../data/rooster.midres.stl')
        self.mesh.compute_normals()

        self.actor = PolyActor(mesh=self.mesh, color='white', edge_visibility=True)
        self.add_prop(self.actor)
        self.style = CircleSelection(interactor=self.interactor, on_selected=None)
        self.style.set_mesh(self.mesh)

        self.register_callback(vtk.vtkCommand.RightButtonPressEvent, self.delete_selection)

    def delete_selection(self, caller, event):
        point_idxs = self.style.selection_indexes
        cell_idxs = []
        # Бежим по всем точкам
        for index in point_idxs:
            # Для каждой точки находит включающие ее ячейки
            cell_idxs.extend(face_for_point(self.mesh, index))
        # Избавляемся от дубликатов
        cell_idxs = list(set(cell_idxs))
        # Удаляем ячейки из меша
        delete_cells(self.mesh, cell_idxs)

        # Удаляем актера, демонстрирующего выделение и обновляем меш в стиле взаимодействия
        self.remove_prop(self.style.selection_actor)
        self.style.selection_actor = None
        self.style.set_mesh(self.mesh)
        self.rwindow.Render()

app = App()
app.run()