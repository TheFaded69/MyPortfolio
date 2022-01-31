import math

import vtk
import numpy as np

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QWidget, QFileDialog, QListWidgetItem, QProgressDialog, QLabel

from libcore.qt import Viewport
from libcore.display import PolyActor
from libcore.mesh import Mesh
from libcore.mixins import ViewportMixin
from libcore.geometry import vec_add, point_distance, fit_implant
from libcore.widget import CubeManipulator

from ..models.image import imageModel
from ..models.stage import stageModel
from ..models.mounter import mounterModel
from ..models.printer import printerModel
from ..models.look import lookModel

from ..views.mounter_ui import Ui_Mounter


class Mounter(QWidget, Ui_Mounter):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
        self.viewport = Viewport()
        self.viewport.istyle = vtk.vtkInteractorStyleTrackballCamera()
        self.viewport.interactor.Initialize()
        self.layout.addWidget(self.viewport)

        self.wCreate.setVisible(False)
        self.wLoad.setVisible(False)

        self._mounts = []
        self._cylinders = []

        self.implant = None
        self.mesh2 = None
        self.len_points = 1

        self.lookModel = lookModel
        self.lookModel.lookUpdated.connect(self.updateLook)

        self.mounterModel = mounterModel
        self.mounterModel.loaded.connect(self.loadMesh)

        self.printerModel = printerModel

        self.stageModel = stageModel

        self.imageModel = imageModel
        self.imageModel.imageLoaded.connect(self.groupBox_2.show)

        self.groupBox_2.hide()

        self.groupBox_3.hide()
        self.pbCylDelete.hide()

    @pyqtSlot(tuple)
    def updateLook(self, look):
        self.viewport.look_from(look)

    def loadMesh(self):
        log = open('C:/Users/Public/Documents/log_file.txt','a')
        log.write('loadMesh'+'\n')
        log.close()
        if self.mounterModel.mesh and self.mounterModel.implant:
            self.actor = PolyActor(self.mounterModel.full_mesh,
                                   color="white",
                                   opacity=0.7)
            self.viewport.add_prop(self.actor)

            self.actor_implant = PolyActor(self.mounterModel.implant,
                                           color="green")
            self.viewport.add_prop(self.actor_implant)

            self.viewport.reset_view()

    def on_char(self, caller, event):
        print('on_char!!!')
        if hasattr(self, '_widget'):
            polyline = self._widget.points
        else:
            return
        if (len(polyline.points) > 1) and (self.len_points != len(polyline.points)):
            self.len_points = len(polyline.points)
            print('Number of points before: {}'.format(len(polyline.points)))
            polyline2 = interpolate_polyline(polyline,
                                             subdivisions=256)
            print('Number of points after: {}'.format(len(polyline.points)))
            polyline2 = choose_closest(polyline2,
                                       self.mounterModel.mesh,
                                       maximum_distance=self.dsbMaximumDistance.value())
            print('Number of points after choose closest: {}'.format(
                len(polyline2.points)))

            polyline2 = thin_out(polyline2,
                                 minimum_step=self.dsbMinimumStep.value())
            print('Number of points after thin out: {}'.format(
                len(polyline2.points)))

            tube = make_ribbon(polyline, width=self.dsbWidth.value())
            tube.smooth(iterations=10, inplace=True)
            tube = normal_extrude(tube, length=self.dsbLength.value())
            # tube.subdivide(levels=3, algorithm='linear', inplace=True)

            if hasattr(self, '_tube_actor'):
                self.viewport.remove_prop(self._tube_actor)
            self._tube_actor = PolyActor(mesh=tube, color='blue', opacity=0.6)
            self.viewport.add_prop(self._tube_actor)

            for cyl in self._cylinders:
                self.viewport.remove_prop(cyl)
            self._cylinders = []

            for pt in polyline2.points:
                cyl_pt_1 = pt
                cyl_pt_2 = vec_add(pt,
                                   [self.dsbLength.value() * x for x in get_normal(self.mounterModel.full_mesh, pt)])
                cyl = mega_tube_old(pt,
                                cyl_pt_2,
                                float(self.dsbDiameter.value()) / 2.,
                                float(self.dsbLength_2.value()))
                                # d1=float(self.cbD1.currentText()),
                                # d2=self.dsbD2.value(),
                                # K=(self.dsbK.value()/100.0))

                self._cylinders.append(PolyActor(mesh=cyl,
                                                 color='white',
                                                 edge_visibility=False))

            for cyl in self._cylinders:
                self.viewport.add_prop(cyl)

    @pyqtSlot(float)
    def on_dsbDiameter_valueChanged(self, value):
        log = open('C:/Users/Public/Documents/log_file.txt','a')
        log.write('Изменение диаметра отверстия'+'\n')
        log.close()
        self.on_char(None, None)

    @pyqtSlot(float)
    def on_dsbLength_2_valueChanged(self, value):
        log = open('C:/Users/Public/Documents/log_file.txt','a')
        log.write('Изменение длины отверстия'+'\n')
        log.close()
        self.on_char(None, None)

    @pyqtSlot(float)
    def on_dsbWidth_valueChanged(self, value):
        log = open('C:/Users/Public/Documents/log_file.txt','a')
        log.write('Изменение ширины'+'\n')
        log.close()
        self.on_char(None, None)

    @pyqtSlot(float)
    def on_dsbLength_valueChanged(self, value):
        log = open('C:/Users/Public/Documents/log_file.txt','a')
        log.write('Изменение высоты'+'\n')
        log.close()
        self.on_char(None, None)

    def on_cbD1_currentTextChanged(self, value):
        self.on_char(None, None)

    @pyqtSlot(float)
    def on_dsbD2_valueChanged(self, value):
        self.on_char(None, None)

    @pyqtSlot(float)
    def on_dsbK_valueChanged(self, value):
        self.on_char(None, None)

    @pyqtSlot(float)
    def on_dsbMinimumStep_valueChanged(self, value):
        self.on_char(None, None)

    @pyqtSlot(float)
    def on_dsbMaximumDistance_valueChanged(self, value):
        self.on_char(None, None)


    @pyqtSlot()
    def on_pbROY_clicked(self):
        mount_index = self.listWidget.currentRow()
        actor = self._mounts[mount_index]['tube']
        actor.mesh.rotate_y(1, inplace=True)
        self.viewport.rwindow.Render()


    @pyqtSlot()
    def on_pbLOY_clicked(self):
        mount_index = self.listWidget.currentRow()
        actor = self._mounts[mount_index]['tube']
        actor.mesh.rotate_y(-1, inplace=True)
        self.viewport.rwindow.Render()


    @pyqtSlot()
    def on_pbROX_clicked(self):
        mount_index = self.listWidget.currentRow()
        actor = self._mounts[mount_index]['tube']
        actor.mesh.rotate_x(1, inplace=True)
        self.viewport.rwindow.Render()


    @pyqtSlot()
    def on_pbLOX_clicked(self):
        mount_index = self.listWidget.currentRow()
        actor = self._mounts[mount_index]['tube']
        actor.mesh.rotate_x(-1, inplace=True)
        self.viewport.rwindow.Render()

    @pyqtSlot(QListWidgetItem, QListWidgetItem)
    def on_listWidget_currentItemChanged(self, item, previous):
        index = self.listWidget.row(item)
        index_prev = self.listWidget.row(previous)
        cyl_index = self.listWidgetCyl.currentRow()

        self.listWidgetCyl.clear()
        for cyl in self._mounts[index]['cylinders']:
            self.listWidgetCyl.addItem('винт')

        if hasattr(self, '_tool_cylinder') and index_prev > -1:
            self.viewport.remove_prop(self._mounts[index_prev]['cylinders'][cyl_index])
            self._mounts[index_prev]['cylinders'][cyl_index] = PolyActor(self._tool_cylinder.mesh)
            self.viewport.add_prop(self._mounts[index_prev]['cylinders'][cyl_index])
            self._tool_cylinder.hide()
            del self._tool_cylinder

        if hasattr(self, '_tool_mount') and index_prev > -1:
            self.viewport.remove_prop(self._mounts[index_prev]['tube'])
            self._mounts[index_prev]['tube'] = PolyActor(self._tool_mount.mesh)
            self.viewport.add_prop(self._mounts[index_prev]['tube'])
            self._tool_mount.hide()
            del self._tool_mount

        if index > -1:
            self._tool_mount = CubeManipulator(interactor=self.viewport.interactor,
                                               actor=self._mounts[index]['tube'])
            self._tool_mount.show()

        for i in self._mounts:
            i['tube'].color = 'blue'
            for cyl in i['cylinders']:
                cyl.color = 'white'
        self._mounts[index]['tube'].color = 'green'

        self.pbDelete.setEnabled(True)
        self.groupBox_3.show()
        self.pbCylDelete.show()

        self.viewport.rwindow.Render()

    @pyqtSlot(QListWidgetItem, QListWidgetItem)
    def on_listWidgetCyl_currentItemChanged(self, item, previous):
        mount_index = self.listWidget.currentRow()
        index = self.listWidgetCyl.row(item)
        index_prev = self.listWidgetCyl.row(previous)

        if hasattr(self, '_tool_mount') and mount_index > -1:
            self.viewport.remove_prop(self._mounts[mount_index]['tube'])
            self._mounts[mount_index]['tube'] = PolyActor(self._tool_mount.mesh)
            self.viewport.add_prop(self._mounts[mount_index]['tube'])
            self._tool_mount.hide()
            del self._tool_mount

        if hasattr(self, '_tool_cylinder') and mount_index > -1:
            self.viewport.remove_prop(self._mounts[mount_index]['cylinders'][index_prev])
            self._mounts[mount_index]['cylinders'][index_prev] = PolyActor(self._tool_cylinder.mesh)
            self.viewport.add_prop(self._mounts[mount_index]['cylinders'][index_prev])
            self._tool_cylinder.hide()
            del self._tool_cylinder

        if index > -1:
            self._tool_cylinder = CubeManipulator(interactor=self.viewport.interactor,
                                                  actor=self._mounts[mount_index]['cylinders'][index])
            self._tool_cylinder.show()

        for cyl in self._mounts[mount_index]['cylinders']:
            cyl.color = 'white'
        self._mounts[mount_index]['cylinders'][index].color = 'red'

        self.pbCylDelete.setEnabled(True)

        self.viewport.rwindow.Render()

    def on_pbCylDelete_pressed(self):
        log = open('C:/Users/Public/Documents/log_file.txt','a')
        log.write('Удалить винт'+'\n')
        log.close()
        mount_index = self.listWidget.currentRow()
        index = self.listWidgetCyl.currentRow()
        cyl_index = self.listWidgetCyl.currentRow()

        if hasattr(self, '_tool_cylinder') and mount_index > -1:
            self.viewport.remove_prop(self._mounts[mount_index]['cylinders'][cyl_index])
            self._mounts[mount_index]['cylinders'][cyl_index] = PolyActor(self._tool_cylinder.mesh)
            self.viewport.add_prop(self._mounts[mount_index]['cylinders'][cyl_index])
            self._tool_cylinder.hide()
            del self._tool_cylinder

        if hasattr(self, '_tool_mount') and mount_index > -1:
            self.viewport.remove_prop(self._mounts[mount_index]['tube'])
            self._mounts[mount_index]['tube'] = PolyActor(self._tool_mount.mesh)
            self.viewport.add_prop(self._mounts[mount_index]['tube'])
            self._tool_mount.hide()
            del self._tool_mount

        self.viewport.remove_prop(self._mounts[mount_index]['cylinders'][index])
        del self._mounts[mount_index]['cylinders'][index]
        self.listWidgetCyl.takeItem(index)

        self.pbCylDelete.setEnabled(False)

        self.viewport.rwindow.Render()

    def on_pbDelete_pressed(self):
        log = open('C:/Users/Public/Documents/log_file.txt','a')
        log.write('Удалить крепление'+'\n')
        log.close()
        self.groupBox_3.hide()
        self.pbCylDelete.hide()

        mount_index = self.listWidget.currentRow()
        cyl_index = self.listWidgetCyl.currentRow()

        if hasattr(self, '_tool_cylinder') and mount_index > -1:
            self.viewport.remove_prop(self._mounts[mount_index]['cylinders'][cyl_index])
            self._mounts[mount_index]['cylinders'][cyl_index] = PolyActor(self._tool_cylinder.mesh)
            self.viewport.add_prop(self._mounts[mount_index]['cylinders'][cyl_index])
            self._tool_cylinder.hide()
            del self._tool_cylinder

        if hasattr(self, '_tool_mount') and mount_index > -1:
            self.viewport.remove_prop(self._mounts[mount_index]['tube'])
            self._mounts[mount_index]['tube'] = PolyActor(self._tool_mount.mesh)
            self.viewport.add_prop(self._mounts[mount_index]['tube'])
            self._tool_mount.hide()
            del self._tool_mount

        self.viewport.remove_prop(self._mounts[mount_index]['tube'])##Тут вернуть index если перестанет работать хд
        for cyl in self._mounts[mount_index]['cylinders']:          ##
            self.viewport.remove_prop(cyl)
        del self._mounts[mount_index]
        self.listWidget.takeItem(mount_index)

        self.pbDelete.setEnabled(False)

        for i in self._mounts:
            i['tube'].color = 'blue'

        self.viewport.rwindow.Render()

    def on_pbCreate_toggled(self, toggle):
        mount_index = self.listWidget.currentRow()

        if hasattr(self, '_tool_mount') and mount_index > -1:
            self.viewport.remove_prop(self._mounts[mount_index]['tube'])
            self._mounts[mount_index]['tube'] = PolyActor(self._tool_mount.mesh)
            self.viewport.add_prop(self._mounts[mount_index]['tube'])
            self._tool_mount.hide()
            del self._tool_mount

        self.listWidget.clearSelection()

        self.groupBox_3.hide()
        self.pbCylDelete.hide()
        self.len_points = 1

        for i in self._mounts:
            i['tube'].color = 'blue'
            for cyl in i['cylinders']:
                cyl.color = 'white'
        self.viewport.rwindow.Render()

        self.pbCreate.setChecked(toggle)
        self.wCreate.setVisible(toggle)

        self._widget = SurfaceProbe(interactor=self.viewport.interactor,
                                    mesh=self.mounterModel.full_mesh,
                                    actor=self.actor)
        self._widget.show()
        self.viewport.register_callback(vtk.vtkCommand.RenderEvent,
                                        self.on_char)

    def on_pbSave_pressed(self):
        log = open('C:/Users/Public/Documents/log_file.txt','a')
        log.write('Сохранить крепление'+'\n')
        log.close()
        self.on_pbCreate_toggled(False)

        if hasattr(self, '_widget') and hasattr(self, '_tube_actor'):
            self._mounts.append({'widget': self._widget,
                                 'tube': self._tube_actor,
                                 'cylinders': self._cylinders})
            for cyl in self._cylinders:
                self.viewport.add_prop(cyl)
            self._cylinders = []
            self._widget.hide()
            del self._widget
            del self._tube_actor

            self.listWidget.addItem('крепление')

    def on_pbLoad_toggled(self, toggle):
        self.listWidget.clearSelection()
        for i in self._mounts:
            i['tube'].color = 'blue'
        self.viewport.rwindow.Render()

        if toggle:
            file_name, _ = QFileDialog.getOpenFileName(self,
                                                       "Открыть STL",
                                                       "",
                                                       "Файлы STL (*.stl)")

            if file_name:
                self.pbLoad.setChecked(True)
                self.wLoad.setVisible(True)
                mesh = Mesh(file_name)
                self.loaded_actor = PolyActor(mesh,
                                              color='green')
                self.viewport.add_prop(self.loaded_actor)
                self.cube_manip = CubeManipulator(self.viewport.interactor,
                                                  self.loaded_actor,
                                                  scaling=False)
                self.cube_manip.show()
        else:
            self.pbLoad.setChecked(False)
            self.wLoad.setVisible(False)

    def on_pbLoadApply_pressed(self):
        log = open('C:/Users/Public/Documents/log_file.txt','a')
        log.write('Загрузить крепление'+'\n')
        log.close()
        self.on_pbLoad_toggled(False)

        if hasattr(self, 'loaded_actor') and hasattr(self, 'cube_manip'):
            mesh = self.cube_manip.mesh
            fitted = fit_implant(implant=mesh,
                                 bone=self.mounterModel.full_mesh)

            self._tube_actor = PolyActor(fitted, color='blue')
            self.viewport.add_prop(self._tube_actor)

            self.viewport.remove_prop(self.loaded_actor)

            self._mounts.append({'widget': None,
                                 'tube': self._tube_actor})
            self.cube_manip.hide()
            del self.cube_manip
            del self.loaded_actor

            self.listWidget.addItem('крепление l')

    def on_pbNext_pressed(self):
        log = open('C:/Users/Public/Documents/log_file.txt','a')
        log.write('Переход на следующий этап'+'\n')
        log.close()
        mount_index = self.listWidget.currentRow()

        if hasattr(self, '_tool_mount'):
            self.viewport.remove_prop(self._mounts[mount_index]['tube'])
            self._mounts[mount_index]['tube'] = PolyActor(self._tool_mount.mesh)
            self.viewport.add_prop(self._mounts[mount_index]['tube'])
            self._tool_mount.hide()
            del self._tool_mount

        if self.mounterModel.implant:
            # pd = QProgressDialog(self)
            # pd.setMinimum(0)
            # pd.setMaximum(100)
            # pd.setValue(0)
            # pd.resize(500, 100)
            # pd.setLabel(QLabel("Объединение креплений и импланта...", pd))
            # pd.show()


            mounts = []
            cylinders = []
            for tube in self._mounts:               
                for cyl in tube['cylinders']:
                    cylinders.append(cyl.mesh)
                # if self.cbCombine.isChecked():
                #     mounts.append(implicitly_combine(main=tube['tube'].mesh,
                #                                      to_subtract_list=cylinders,
                #                                      to_add_list=[]))
                # else:
                mounts.append(tube['tube'].mesh)
            mounts.append(self.mounterModel.implant)

            implant = Mesh.from_meshes(mounts)
            cylinders = Mesh.from_meshes(cylinders)
            # callback = lambda caller, id: pd.setValue(
            #     round(caller.GetProgress() * 100))
            callback = None
            # if self.cbImplicitize.checkState():
            #     implant = implicitize(implant, callback=callback)
            self.printerModel.cylinders = cylinders
            self.printerModel.implant = implant

        self.stageModel.stage = 7

    def on_pbApply_pressed(self):
        log = open('C:/Users/Public/Documents/log_file.txt','a')
        log.write('Удалить (возможно плотность ткани)'+'\n')
        log.close()
        self.viewport.remove_prop(self.mesh2)
        mesh2 = self.imageModel.image.extract_surface(threshold=self.spinBox.value())
        self.mesh2 = PolyActor(mesh2, color='red', opacity=0.4)
        self.viewport.add_prop(self.mesh2)

    def on_pbDelete2_pressed(self):
        self.viewport.remove_prop(self.mesh2)


def get_normal(mesh, point):
    pt_idx = mesh.find_closest_point(point)
    normal = mesh.normals[pt_idx]
    return [-x for x in normal]


def mega_tube_old(pt1, pt2, radius=0.8, length=5.0):
    source = vtk.vtkLineSource()
    source.SetPoint1(pt1 + length * np.linalg.norm(pt2 - pt1))
    source.SetPoint2(pt2)
    source.Update()

    tube_filter = vtk.vtkTubeFilter()
    tube_filter.SetInputData(source.GetOutput())
    tube_filter.SetCapping(True)
    tube_filter.SetRadius(radius)
    tube_filter.SetNumberOfSides(24)
    tube_filter.Update()
    return Mesh(tube_filter.GetOutput())



# def mega_tube(pt1, pt2, radius, d1=0.8, d2=1.2, K=0.1):
#     d1 = radius
#     source = vtk.vtkLineSource()
#     source.SetPoint1(pt1)
#     source.SetPoint2(pt2)
#     source.Update()

#     tube_filter = vtk.vtkTubeFilter()
#     tube_filter.SetInputData(source.GetOutput())
#     tube_filter.SetCapping(True)
#     tube_filter.SetRadius(d1)
#     tube_filter.SetNumberOfSides(24)
#     tube_filter.Update()

#     cone_source = vtk.vtkConeSource()
#     cone_source.SetRadius(d1)
#     cone_source.SetResolution(60)
#     cone_source.SetHeight(K*10)
#     cone_source.SetAngle(87)
#     cone_source.SetCapping(True)
#     direction = (pt2[0] - pt1[0],
#                  pt2[1] - pt1[1],
#                  pt2[2] - pt1[2])
#     direction = np.array(direction) / np.linalg.norm(direction)
#     cone_source.SetDirection(pt2[0] - pt1[0],
#                              pt2[1] - pt1[1],
#                              pt2[2] - pt1[2])
#     print()
#     cone_source.SetCenter(pt2)
#     cone_source.Update()

#     append_filter = vtk.vtkAppendPolyData()
#     append_filter.AddInputData(tube_filter.GetOutput())
#     append_filter.AddInputData(cone_source.GetOutput())
#     append_filter.Update()

#     clean_filter = vtk.vtkCleanPolyData()
#     clean_filter.SetInputData(append_filter.GetOutput())
#     clean_filter.Update()

#     return Mesh(clean_filter.GetOutput())


def mega_tube(pt1, pt2, d1=0.2, d2=0.3, K=0.4):
    NUM_DOTS = 256
    source = vtk.vtkLineSource()
    source.SetPoint1(pt1)
    source.SetPoint2(pt2)
    source.Update()

    spline = vtk.vtkSplineFilter()
    spline.SetInputData(source.GetOutput())
    spline.SetSubdivideToSpecified()
    spline.SetNumberOfSubdivisions(NUM_DOTS)
    spline.Update()

    radii = vtk.vtkDoubleArray()
    radii.SetNumberOfValues(NUM_DOTS+1)
    border = int((1-K)*NUM_DOTS)
    for idx in range(NUM_DOTS+1):
        if idx < border:
            radii.SetValue(idx, d1)
        else:
            x = (idx-border)/(NUM_DOTS-border)
            y = d1 + (d2/d1)*x
            print(x, y)
            radii.SetValue(idx, y)

    mesh = Mesh(spline.GetOutput())
    mesh.GetPointData().SetScalars(radii)
    tube_filter = vtk.vtkTubeFilter()
    tube_filter.SetInputData(mesh)
    tube_filter.SetCapping(True)
    tube_filter.SetRadius(d1)
    tube_filter.SetVaryRadiusToVaryRadiusByScalar()
    tube_filter.SetNumberOfSides(32)
    tube_filter.SetRadiusFactor(d2/d1)


    #tube_filter.SetVaryRadiusToVaryRadiusByScalar()
    #tube_filter.SetVaryRadiusToVaryRadiusByAbsoluteScalar()
    #tube_filter.SetVaryRadius()
    tube_filter.Update()

    return Mesh(tube_filter.GetOutput())


def make_ribbon(polyline, width=2.0):
    """Делает из линии ленту нулевой толщины и заданной ширины"""
    ribbon_filter = vtk.vtkRibbonFilter()
    ribbon_filter.SetInputData(polyline)
    ribbon_filter.SetWidth(width)
    ribbon_filter.Update()
    result = Mesh(ribbon_filter.GetOutput())
    return result


def normal_extrude(mesh, length=1.0):
    mesh.compute_normals()
    extruder = vtk.vtkLinearExtrusionFilter()
    extruder.SetInputData(mesh)
    extruder.SetExtrusionTypeToNormalExtrusion()
    extruder.SetCapping(True)
    extruder.SetScaleFactor(length)
    extruder.Update()
    return Mesh(extruder.GetOutput())


def implicitize(mesh, value=0.01):
    """Запускать при окончательной подготовке импланта"""
    implicit = vtk.vtkImplicitPolyDataDistance()
    implicit.SetInput(mesh)

    sample = vtk.vtkSampleFunction()
    sample.SetImplicitFunction(implicit)
    sample.SetModelBounds(*mesh.bounds)
    sample.SetSampleDimensions(120, 120, 120)
    sample.CappingOff()

    surface = vtk.vtkContourFilter()
    surface.SetInputConnection(sample.GetOutputPort())
    surface.SetValue(0, value)
    surface.ComputeNormalsOn()
    surface.ComputeGradientsOn()
    surface.Update()

    return Mesh(surface.GetOutput())


def to_implicit(mesh):
    imp = vtk.vtkImplicitPolyDataDistance()
    imp.SetInput(mesh)
    return imp


def implicitly_combine(main, to_add_list, to_subtract_list):
    all_meshes = [main]
    all_meshes.extend(to_add_list)
    all_meshes.extend(to_subtract_list)
    all_mesh = Mesh.from_meshes(all_meshes)
    bounding_box = all_mesh.bounds
    del all_mesh

    main_imp = to_implicit(main)
    to_add_imp = [to_implicit(mesh) for mesh in to_add_list]
    to_subtract_imp = [to_implicit(mesh) for mesh in to_subtract_list]

    boolean_sum = vtk.vtkImplicitBoolean()
    boolean_sum.SetOperationTypeToUnion()
    boolean_sum.AddFunction(main_imp)
    for mesh in to_add_imp:
        boolean_sum.AddFunction(mesh)

    boolean_diff = vtk.vtkImplicitBoolean()
    boolean_diff.SetOperationTypeToDifference()
    boolean_diff.AddFunction(boolean_sum)
    for mesh in to_subtract_imp:
        boolean_diff.AddFunction(mesh)

    sampler = vtk.vtkSampleFunction()
    sampler.SetImplicitFunction(boolean_diff)
    sampler.SetModelBounds(bounding_box)
    sampler.SetSampleDimensions(120, 120, 120)

    surface = vtk.vtkContourFilter()
    surface.SetInputConnection(sampler.GetOutputPort())
    surface.SetValue(0, 0.001)
    surface.Update()

    return Mesh(surface.GetOutput())


def interpolate_polyline(polyline, subdivisions=256):
    spline = vtk.vtkSplineFilter()
    spline.SetInputData(polyline)
    spline.SetSubdivideToSpecified()
    spline.SetNumberOfSubdivisions(256)
    spline.Update()
    return Mesh(spline.GetOutput())

class SurfaceProbe(object):

    def __init__(self, interactor, mesh, actor):
        self.interactor = interactor
        self.mesh = mesh

        self.point_placer = vtk.vtkPolygonalSurfacePointPlacer()
        self.point_placer.GetPolys().AddItem(mesh)
        self.point_placer.AddProp(actor)
        self.point_placer.SnapToClosestPointOn()

        self.widget = vtk.vtkContourWidget()
        self.widget.SetInteractor(interactor)
        self.widget.SetPriority(1.0)

        self.representation = self.widget.GetRepresentation()
        self.representation.AlwaysOnTopOn()
        self.representation.SetLineInterpolator(vtk.vtkLinearContourLineInterpolator())
        self.representation.GetLinesProperty().RenderPointsAsSpheresOn()
        self.representation.SetPointPlacer(self.point_placer)

    @property
    def points(self):
        return Mesh(self.representation.GetContourRepresentationAsPolyData())

    def show(self):
        self.widget.On()

    def hide(self):
        self.widget.Off()


def choose_closest(polyline, mesh, maximum_distance=1.0):
    good_points = []
    for pt in polyline.points:
        closest_idx = mesh.find_closest_point(pt)
        closest_point = mesh.points[closest_idx]
        distance = point_distance(pt, closest_point)
        if distance < maximum_distance:
            good_points.append(pt)
    return Mesh.from_points(good_points)


def thin_out(polyline, minimum_step=10.0):
    good_points = []
    first_point, last_point = polyline.points[1], polyline.points[-1]
    good_points.append(first_point)
    current_point = first_point
    for pt in polyline.points:
        distance = point_distance(current_point, pt)
        if distance >= minimum_step:
            good_points.append(pt)
            current_point = pt
    good_points.append(last_point)
    return Mesh.from_points(good_points)
