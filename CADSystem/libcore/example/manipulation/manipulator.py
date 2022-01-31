import vtk

import numpy as np
from libcore.mixins import ViewportMixin
from libcore.display import PolyActor
from libcore.mesh import Mesh
from libcore.interact import StyleRubberBand2D
from libcore.widget import ArrowProbe
from libcore.geometry import vec_add, vec_normalize, vec_norm
from libcore.geometry import point_distance

class App(ViewportMixin):

    def __init__(self):
        super().__init__()

        self.mesh = Mesh('../../data/rooster.midres.stl')
        self.mesh.compute_normals()
        self.actor = PolyActor(mesh=self.mesh, color='green', edge_visibility=True)
        self.selected_actor = None
        self.add_prop(self.actor)

        point = self.mesh.points[0]
        self.arrow = ArrowProbe(interactor=self.interactor,
                                origin=point, on_changed=self.on_arrow)


        picker = vtk.vtkAreaPicker()
        self.interactor.SetPicker(picker)
        self.selection_style = StyleRubberBand2D(on_selection=self.on_selection)
        self.manipulation_style = vtk.vtkInteractorStyleTrackballCamera()
        self.style = self.selection_style
        self.selected_indexes = []
        self.register_callback(vtk.vtkCommand.CharEvent, self.on_char)

    def on_char(self, caller, event):
        key = self.interactor.GetKeySym()
        if key == '1':
            self.style = self.selection_style
        elif key == '2':
            self.style = self.manipulation_style
        elif key == '3':
            warp_vectors = [list([0.0, 0.0, 0.0]) for idx in range(self.mesh.number_of_points)]
            for idx in self.selected_indexes:
                warp_vectors[idx] = self.arrow.direction
            self.mesh.warp(vecs=warp_vectors, inplace=True)
            if self.selected_actor:
                self.remove_prop(self.selected_actor)
                self.selected_actor = None
            self.rwindow.Render()
        elif key == '4':
            warp_vectors = [list([0.0, 0.0, 0.0]) for idx in range(self.mesh.number_of_points)]
            center = self.arrow.point1
            direction = vec_normalize(self.arrow.direction)
            length = vec_norm(self.arrow.direction)
            for idx in self.selected_indexes:
                point = self.mesh.points[idx]
                dist = point_distance(center, point)
                warp_vectors[idx] = [(length-dist)*n for n in direction]
            self.mesh.warp(vecs=warp_vectors, inplace=True)
            if self.selected_actor:
                self.remove_prop(self.selected_actor)
                self.selected_actor = None
            self.rwindow.Render()

    def on_selection(self, frustum):
        # Добавить скалярный массив с индексами в первоначальные данные
        id_filter = vtk.vtkIdFilter()
        id_filter.SetInputData(self.mesh)
        id_filter.PointIdsOn()
        id_filter.SetIdsArrayName("OriginalIds")
        id_filter.Update()
        surface_filter = vtk.vtkDataSetSurfaceFilter()
        surface_filter.SetInputConnection(id_filter.GetOutputPort())
        surface_filter.Update()

        # Найти видимые точки

        visible_selector = vtk.vtkSelectVisiblePoints()
        visible_selector.SetInputData(surface_filter.GetOutput())
        visible_selector.SetRenderer(self.renderer)
        visible_selector.Update()

        # Взять точки попадающие в выделение
        extract_poly_data_geometry = vtk.vtkExtractPolyDataGeometry()
        extract_poly_data_geometry.SetInputData(visible_selector.GetOutput())
        extract_poly_data_geometry.SetImplicitFunction(frustum)
        extract_poly_data_geometry.Update()
        selected_points = Mesh(extract_poly_data_geometry.GetOutput())

        # Создать меш для подсвечивания
        if self.selected_actor:
            self.remove_prop(self.selected_actor)
        self.selected_actor = PolyActor(mesh=selected_points, color='green', vertex_visibility=True, point_size=4.0)
        self.add_prop(self.selected_actor)

        # Узнать индексы выбранных точек
        self.selected_indexes.clear()
        idx_array = selected_points.GetPointData().GetArray("OriginalIds")
        for i in range(idx_array.GetNumberOfValues()):
            self.selected_indexes.append(idx_array.GetValue(i))

        # Включить виджет с точкой
        self.arrow.point1 = selected_points.center
        normals = np.array(self.mesh.normals[self.selected_indexes])
        point2 = list(np.array(selected_points.center) + 10*normals.mean(axis=0))
        self.arrow.point2 = point2

        #print('actually', self.arrow.point1)
        #print('actually', self.arrow.point2)

        print('should be', selected_points.center)
        print('should be', point2)

        self.arrow.show()

        # Выключаем режим
        self.style = self.manipulation_style

        self.rwindow.Render()

    def on_arrow(self):
        # print('direction', self.arrow.direction)
        # print('point1', self.arrow.point1)
        # print('point2', self.arrow.point2)
        pass


app = App()
app.run()