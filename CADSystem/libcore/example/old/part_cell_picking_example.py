import vtk

from libcore import Mesh
from libcore.display import PolyActor
from libcore.mixins import ViewportMixin
from libcore.topology import delete_cells, cell_neighbors, list_to_ids



# Catch mouse events
class MouseInteractorStyle(vtk.vtkInteractorStyleRubberBandPick):

    def __init__(self):
        # мэппер для отображения выбранных ячеек
        self.selected_mapper = vtk.vtkDataSetMapper()
        # актер для отображения выбранных ячеек
        self.selected_actor = vtk.vtkActor()
        self.data = None
        self.cell = None
        self.AddObserver(vtk.vtkCommand.LeftButtonPressEvent, self.on_left_button_down)

    def on_left_button_down(self, caller, event):
        # Get the location of the click (in window coordinates)
        pos = self.GetInteractor().GetEventPosition()

        picker = vtk.vtkCellPicker()
        picker.SetTolerance(0.0005)

        # Pick from this location.
        picker.Pick(pos[0], pos[1], 0, self.GetDefaultRenderer())

        world_position = picker.GetPickPosition()
        self.cell = picker.GetCellId()
        print("Cell id is: ", picker.GetCellId())

        cells = cell_neighbors(self.data, self.cell)

        if (picker.GetCellId() != -1):
            print("Pick position is: ", world_position[0], " ", world_position[1], " ", world_position[2])
            ids = list_to_ids(cells)

            selection_node = vtk.vtkSelectionNode()
            selection_node.SetFieldType(vtk.vtkSelectionNode.CELL)
            selection_node.SetContentType(vtk.vtkSelectionNode.INDICES)
            selection_node.SetSelectionList(ids)

            selection = vtk.vtkSelection()
            selection.AddNode(selection_node)

            extract_selection = vtk.vtkExtractSelection()
            extract_selection.SetInputData(0, self.data)
            extract_selection.SetInputData(1, selection)
            extract_selection.Update()

            # In selection
            selected = vtk.vtkUnstructuredGrid()
            selected.ShallowCopy(extract_selection.GetOutput())

            print("There are ", selected.GetNumberOfPoints(), " points in the selection.")
            print("There are ", selected.GetNumberOfCells(), " cells in the selection.")

            self.selected_mapper.SetInputData(selected)
            self.selected_actor.SetMapper(self.selected_mapper)
            self.selected_actor.GetProperty().EdgeVisibilityOn()
            self.selected_actor.GetProperty().SetEdgeColor(1, 0, 0)
            self.selected_actor.GetProperty().SetLineWidth(5)

            self.GetInteractor().GetRenderWindow().GetRenderers().GetFirstRenderer().AddActor(self.selected_actor)

        self.OnLeftButtonDown()


class App(ViewportMixin):

    def __init__(self):
        super().__init__()
        self.mesh = Mesh('../data/rooster.midres.stl')
        self.mesh_actor = PolyActor(mesh=self.mesh, color='green', edge_color='black', edge_visibility=True, opacity=1.0)
        self.add_prop(self.mesh_actor)

        self.style = MouseInteractorStyle()
        self.style.SetDefaultRenderer(self.renderer)
        self.style.data = self.mesh

        self.area_picker = vtk.vtkAreaPicker()

        self.interactor.SetPicker(self.area_picker)
        self.interactor.SetInteractorStyle(self.style)
        self.interactor.AddObserver(vtk.vtkCommand.EndPickEvent, self.end_pick)

    def user(self):
        delete_cells(self.mesh, [self.style.cell])
        self.renderer.RemoveActor(self.style.selected_actor)
        self.window.Render()

    def end_pick(self, caller, event):
        frustum = self.interactor.GetPicker().GetFrustum()
        self.mesh.overwrite(self.mesh.extract(frustum, inverse=True))
        self.renderer.Render()


app = App()
app.run()

