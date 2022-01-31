import vtk
import math
import numpy

from PyQt5.QtCore import pyqtSlot, pyqtSignal, QObject, Qt
from PyQt5.QtWidgets import QWidget

from libcore.display import PolyActor
from libcore.qt import Viewport
from libcore.interact import StyleDrawPolygon3, StyleActorSelection, StyleRubberBand2D, CircleSelection
from libcore.color import get_color
from libcore.widget import Label, PlaneSelector, CubeManipulator
from libcore.geometry import Plane
from libcore.mesh import Mesh
from libcore.topology import delete_cells
from libcore.topology import face_for_point

from ..models.editor import editorModel
from ..models.look import lookModel
from ..models.mirrorer import mirrorerModel
from ..models.implantor import implantorModel
from ..models.stage import stageModel

from ..views.editor_ui import Ui_Editor


class Editor(QWidget, Ui_Editor):
    previewdialog = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)

        self.crossSectionActors = []
        self._tool_parts = []
        self._tool_precut = None
        self._tool_cube = None
        self._tool_sphere = None
        self._tool_plane = None

        self.viewport = Viewport()
        self.viewport.istyle = vtk.vtkInteractorStyleTrackballCamera()
        self.viewport.interactor.Initialize()
        self.layout.addWidget(self.viewport)
        self.viewport.interactor.AddObserver(vtk.vtkCommand.CharEvent,
                                             self.callback)

        self.editorModel = editorModel
        self.editorModel.propSelected.connect(self.updateRender)
        self.editorModel.propSelected.connect(self.updateManip)
        self.editorModel.propsUpdated.connect(self.updateProps)
        self.editorModel.cutterPolyline.toolUpdated.connect(self.updateTool)
        self.editorModel.cutterRect.toolUpdated.connect(self.updateTool)
        self.editorModel.cutterCircle.toolUpdated.connect(self.updateTool)
        self.editorModel.cutterCircle.cutUpdated.connect(self.cutCircle)
        self.editorModel.cutterCube.toolUpdated.connect(self.updateTool)
        self.editorModel.cutterSphere.toolUpdated.connect(self.updateTool)
        self.editorModel.cutterSphere.cutUpdated.connect(self.cutSphere)
        self.editorModel.cutterPlane.toolUpdated.connect(self.updateTool)
        self.editorModel.cutterPlane.cutUpdated.connect(self.cutPlane)
        self.editorModel.splitter.toolUpdated.connect(self.updateTool)

        self.editorModel.crossSectionUpdated.connect(
            self.updateCrossSectionTool)
        self.editorModel.ruler3DUpdated.connect(self.updateRuler3DTool)

        self.lookModel = lookModel
        self.lookModel.lookUpdated.connect(self.updateLook)

        self.mirrorerModel = mirrorerModel

        self.implantorModel = implantorModel

        self.stageModel = stageModel

        self.widget_2.setVisible(False)

    def callback(self, caller, event):
        if self.viewport.interactor.GetKeySym() == 'Escape':
            if self.rbTool.isChecked():
                self.on_rbCamera_toggled(True)
            elif self.rbTool.isEnabled():
                self.on_rbTool_toggled(True)

    @pyqtSlot()
    def updateRender(self):
        self.viewport.rwindow.Render()

    def updateCrossSectionTool(self, toggle):
        if toggle:
            self.editorModel.cutterPolyline.toggle = False
            self.editorModel.cutterRect.toggle = False
            self.editorModel.cutterCircle.toggle = False
            self.editorModel.cutterCube.toggle = False
            self.editorModel.cutterSphere.toggle = False
            self.editorModel.cutterPlane.toggle = False

            for prop in self.editorModel.props:
                self.editorModel.props[prop].opacity = 0.23

            a = list(self.editorModel.props.keys())
            while a:
                i = a.pop(0)
                for j in a:
                    mesh = self.editorModel.props[j].mesh.slice_by_mesh(
                        self.editorModel.props[i].mesh)
                    actor = PolyActor(mesh=mesh,
                                      color=self.editorModel.props[j].color,
                                      render_lines_as_tubes=True,
                                      line_width=5.0,
                                      opacity=1.0)
                    print(actor)
                    self.viewport.renderer.AddActor(actor)
                    self.crossSectionActors.append(actor)
        else:
            for prop in self.editorModel.props:
                if self.editorModel.props[prop].opacity == 0.23:
                    self.editorModel.props[prop].opacity = 1.0
            while self.crossSectionActors:
                prop = self.crossSectionActors.pop(0)
                self.viewport.renderer.RemoveActor(prop)

        self.viewport.rwindow.Render()

    def updateRuler3DTool(self, toggle):
        if toggle:
            self.editorModel.cutterPolyline.toggle = False
            self.editorModel.cutterRect.toggle = False
            self.editorModel.cutterCircle.toggle = False
            self.editorModel.cutterCube.toggle = False
            self.editorModel.cutterSphere.toggle = False
            self.editorModel.cutterPlane.toggle = False

            self.widget_ruler3d = vtk.vtkLineWidget2()
            self.widget_ruler3d.SetInteractor(self.viewport.interactor)
            self.widget_ruler3d.CreateDefaultRepresentation()
            rep = self.widget_ruler3d.GetLineRepresentation()
            rep.SetPoint2WorldPosition(numpy.array(rep.GetPoint2WorldPosition()) * 50)
            self.widget_ruler3d.GetLineRepresentation().SetDistanceAnnotationFormat("%-#6.3g mm")
            self.widget_ruler3d.GetLineRepresentation().SetDistanceAnnotationVisibility(True)
            self.widget_ruler3d.AddObserver(vtk.vtkCommand.EndInteractionEvent,
                                            self.ruler3d_callback)
            self.ruler3d_callback(None, None)
            self.widget_ruler3d.On()
        else:
            if hasattr(self, 'widget_ruler3d'):
                self.widget_ruler3d.Off()

        self.viewport.rwindow.Render()

    def ruler3d_callback(self, caller, event):
        distance = self.widget_ruler3d.GetLineRepresentation().GetDistance()
        self.widget_4.lRuler3D.setText('Длина: {:-f} мм'.format(distance))

    @pyqtSlot()
    def updateProps(self):
        for prop in self.viewport.actors():
            self.viewport.remove_prop(prop)
        if self._tool_cube:
            self._tool_cube.hide()
            self._tool_cube.show()

        if self.editorModel.cutterCircle.toggle:
            if self.editorModel.prop in self.editorModel.props:
                mesh = self.editorModel.props[self.editorModel.prop].mesh
                self.viewport.istyle.set_mesh(mesh)

        self.viewport.add_props(self.editorModel.props.values())
        # self.updateRender()

    @pyqtSlot(QObject)
    def updateTool(self, tool):
        if tool.toggle:
            self.on_pbManipulator_toggled(False)
            self.widget_4.on_pbCrossSection_toggled(False)

            self.viewport.renderer.RemoveActor(self._tool_precut)
            if hasattr(tool, 'precut'):
                self._tool_precut = tool.precut
            if hasattr(tool, 'parts'):
                for part in self._tool_parts:
                    self.viewport.remove_prop(part)
                self._tool_parts = tool.parts
        else:
            self.on_rbCamera_toggled(True)
            self.rbTool.setEnabled(False)

            if self._tool_cube:
                self._tool_cube.hide()
                self._tool_cube = None
                if self.editorModel.prop in self.editorModel.props:
                    self.editorModel.props[self.editorModel.prop].opacity = 1.0
            if self._tool_plane:
                self._tool_plane.hide()
                self._tool_plane = None
                self.updateProps()
            if self._tool_sphere:
                self._tool_sphere.hide()
                self._tool_sphere = None
                self.updateProps()
            if tool.name == 'splitter':
                for part in tool.parts:
                    self.viewport.remove_prop(part)
                if self.editorModel.prop in self.editorModel.props:
                    self.viewport.add_prop(self.editorModel.props[
                        self.editorModel.prop])

            self.updateRender()
            return

        if tool.name == 'polyline':
            self.rbTool.setEnabled(True)
            self.on_rbTool_toggled(True)
            self.viewport.renderer.AddActor(self._tool_precut)
        elif tool.name == 'rect':
            self.rbTool.setEnabled(True)
            self.on_rbTool_toggled(True)
            self.viewport.renderer.AddActor(self._tool_precut)
        elif tool.name == 'circle':
            self.rbTool.setEnabled(True)
            self.on_rbTool_toggled(True)
            self.viewport.renderer.AddActor(self._tool_precut)
        elif tool.name == 'cube':
            self.viewport.renderer.AddActor(self._tool_precut)
            if not self._tool_cube:
                prop = self.editorModel.props[self.editorModel.prop]
                self._tool_cube = CubeW(interactor=self.viewport.interactor,
                                        prop=prop,
                                        on_select=tool.update,
                                        cuttools=self.cuttools)
                self._tool_cube.show()
        elif tool.name == 'sphere':
            if not self._tool_sphere:
                self.sphere_mesh = Mesh.sphere(center=(105.202, 99.188, 50.0),
                                               radius=30.0)
                self.sphere_actor = PolyActor(mesh=self.sphere_mesh,
                                              color='green',
                                              opacity=0.5)
                self.viewport.renderer.AddActor(self.sphere_actor)
                self._tool_sphere = CubeManipulator(interactor=self.viewport.interactor,
                                                    actor=self.sphere_actor)
                self._tool_sphere.show()

            # self.viewport.renderer.AddActor(self._tool_precut)
            # if not self._tool_cube:
            #     prop = self.editorModel.props[self.editorModel.prop]
            #     self._tool_cube = CubeW(interactor=self.viewport.interactor,
            #                             prop=prop,
            #                             on_select=tool.update,
            #                             cuttools=self.cuttools)
            #     self._tool_cube.show()
        elif tool.name == 'plane':
            # self.viewport.remove_prop(self.editorModel.props[
            #                           self.editorModel.prop])
            # self.viewport.add_props(tool.parts)
            if not self._tool_plane:
                # prop = self.editorModel.props[self.editorModel.prop]
                # self._tool_plane = PlaneW(interactor=self.viewport.interactor,
                #                           prop=prop,
                #                           on_select=tool.update)
                # self.viewport.remove_prop(self.editorModel.props[
                #                           self.editorModel.prop])
                self._tool_plane = PlaneW(interactor=self.viewport.interactor)
                self._tool_plane.show()

        elif tool.name == 'splitter':
            self.viewport.remove_prop(self.editorModel.props[
                                      self.editorModel.prop])
            self.viewport.add_props(tool.parts)

        self.updateRender()

    def cutPlane(self, tool):
        if self._tool_plane:
            left, right = self._tool_plane.orig.mesh.disect_by_plane(
                self._tool_plane._plane)

            if self.editorModel.cutterPlane.close_mesh:
                left.fill_holes(inplace=True)
                right.fill_holes(inplace=True)

            self.editorModel.addProp(self.editorModel.prop + '.l',
                                     PolyActor(left))
            self.editorModel.addProp(self.editorModel.prop + '.r',
                                     PolyActor(right))
            self.editorModel.delProp()
            self.updateProps()
            self.updateTool(self.editorModel.cutterPlane)
            # self.editorModel.cutterPlane.toggle = False

    def cutSphere(self, tool):
        if self._tool_sphere:
            if self.editorModel.prop in self.editorModel.props:
                prop = self.editorModel.props[self.editorModel.prop]
                self.editorModel.props[self.editorModel.prop] = PolyActor(prop.mesh.clip_by_mesh(self._tool_sphere.mesh,
                                                                                                 inverse=tool.inverse),
                                                                          color=prop.color)
                self.updateProps()

                self.viewport.renderer.AddActor(self.sphere_actor)
                self._tool_sphere = CubeManipulator(interactor=self.viewport.interactor,
                                                    actor=self.sphere_actor)
                self._tool_sphere.show()

    def cutCircle(self, tool):
        if self.editorModel.prop in self.editorModel.props:
            prop = self.editorModel.props[self.editorModel.prop]

            point_idxs = self.viewport.istyle.selection_indexes
            cell_idxs = []

            # Бежим по всем точкам
            for index in point_idxs:
                # Для каждой точки находит включающие ее ячейки
                cell_idxs.extend(face_for_point(prop.mesh, index))
            # Избавляемся от дубликатов
            cell_idxs = list(set(cell_idxs))
            # Удаляем ячейки из меша
            delete_cells(prop.mesh, cell_idxs)

            self.viewport.remove_prop(self.viewport.istyle.selection_actor)
            self.viewport.istyle.selection_actor = None
            self.viewport.istyle.set_mesh(prop.mesh)
            self.viewport.rwindow.Render()

    @pyqtSlot(tuple)
    def updateLook(self, look):
        self.viewport.look_from(look)

    def on_rbCamera_toggled(self, toggle):
        if toggle:
            self.rbCamera.setChecked(True)
            self.viewport.istyle = vtk.vtkInteractorStyleTrackballCamera()

    def on_rbTool_toggled(self, toggle):
        if toggle:
            self.rbTool.setChecked(True)
            cutterPolyline = self.editorModel.cutterPolyline
            cutterRect = self.editorModel.cutterRect
            cutterCircle = self.editorModel.cutterCircle

            if cutterPolyline.toggle:
                self.viewport.istyle = StyleDrawPolygon3(interactor=self.viewport.interactor,
                                                         on_select=cutterPolyline.update)
            if cutterRect.toggle:
                self.viewport.istyle = StyleRubberBand2D(
                    on_selection=cutterRect.update)
            if cutterCircle.toggle:
                self.viewport.istyle = CircleSelection(interactor=self.viewport.interactor,
                                                       on_selected=None)
                if self.editorModel.prop in self.editorModel.props:
                    mesh = self.editorModel.props[self.editorModel.prop].mesh
                    self.viewport.istyle.set_mesh(mesh)

    def on_pbNext_pressed(self):
        meshes = []
        log = open('C:/Users/Public/Documents/log_file.txt','a')
        log.write('Переход на следующий этап'+'\n')
        log.close()

        for prop in self.editorModel.props:
            meshes.append(self.editorModel.props[prop].mesh)
        self.mirrorerModel.mesh = Mesh.from_meshes(meshes)
        self.stageModel.stage = 4

        # if self.editorModel.prop in self.editorModel.props:
        #     mesh = self.editorModel.props[self.editorModel.prop].mesh
        #     self.mirrorerModel.mesh = mesh
        #     self.stageModel.stage = 4

    def on_pbImplant_pressed(self):
        log = open('C:/Users/Public/Documents/log_file.txt','a')
        log.write('Переход на этап импланта'+'\n')
        log.close()

        if self.editorModel.prop in self.editorModel.props:
            mesh = self.editorModel.props[self.editorModel.prop].mesh
            self.implantorModel.addProp('mesh', PolyActor(mesh))
            self.stageModel.stage = 5

    def on_pbPlaneXY_toggled(self, toggle):
        log = open('C:/Users/Public/Documents/log_file.txt','a')
        log.write('Включение\выключение плоскости ХУ'+'\n')
        log.close()

        if toggle:
            if self.editorModel.prop in self.editorModel.props:
                mesh = self.editorModel.props[self.editorModel.prop].mesh
                self.planeXY = PlaneSelector(self.viewport.interactor,
                                             Plane.XY(origin=mesh.center),
                                             mesh.bounds)
                self.planeXY.show()
        else:
            if hasattr(self, 'planeXY'):
                self.planeXY.hide()
                del self.planeXY
        self.viewport.rwindow.Render()

    def on_pbPlaneXZ_toggled(self, toggle):
        log = open('C:/Users/Public/Documents/log_file.txt','a')
        log.write('Включение\выключение плоскости XZ'+'\n')
        log.close()

        if toggle:
            if self.editorModel.prop in self.editorModel.props:
                mesh = self.editorModel.props[self.editorModel.prop].mesh
                self.planeXZ = PlaneSelector(self.viewport.interactor,
                                             Plane.XZ(origin=mesh.center),
                                             mesh.bounds)
                self.planeXZ.show()
        else:
            if hasattr(self, 'planeXZ'):
                self.planeXZ.hide()
                del self.planeXZ
        self.viewport.rwindow.Render()

    def on_pbPlaneYZ_toggled(self, toggle):
        log = open('C:/Users/Public/Documents/log_file.txt','a')
        log.write('Включение\выключение плоскости YZ'+'\n')
        log.close()

        if toggle:
            if self.editorModel.prop in self.editorModel.props:
                mesh = self.editorModel.props[self.editorModel.prop].mesh
                self.planeYZ = PlaneSelector(self.viewport.interactor,
                                             Plane.YZ(origin=mesh.center),
                                             mesh.bounds)
                self.planeYZ.show()
        else:
            if hasattr(self, 'planeYZ'):
                self.planeYZ.hide()
                del self.planeYZ
        self.viewport.rwindow.Render()

    def on_pbManipulator_toggled(self, toggle):
        self.widget_2.setVisible(toggle)
        
        if hasattr(self, 'manipulator_widget'):
            if self._prop in self.editorModel.props:
                self.editorModel.reProp(self._prop,
                                        self.manipulator_widget.mesh)
            self.manipulator_widget.hide()
            del self.manipulator_widget

        if self.editorModel.prop in self.editorModel.props:
            actor = self.editorModel.props[self.editorModel.prop]
            self._prop = self.editorModel.prop

        if toggle:
            if hasattr(self, 'sphere_widget'):
                self.on_pbFlate_toggled(False)
            if self.editorModel.prop in self.editorModel.props:
                actor = self.editorModel.props[self.editorModel.prop]
                self._prop = self.editorModel.prop
                self.manipulator_widget = CubeManipulator(self.viewport.interactor,
                                                          actor)
                self.manipulator_widget.show()
            if not self.pbManipulator.isChecked():
                self.pbManipulator.setChecked(Qt.Checked)
        else:
            if self.pbManipulator.isChecked():
                self.pbManipulator.setChecked(Qt.Unchecked)

    @pyqtSlot()
    def on_pbROY_clicked(self):

        if self.editorModel.prop in self.editorModel.props:
            actor = self.editorModel.props[self.editorModel.prop]
            actor.mesh.rotate_y(1, inplace=True)
            self.manipulator_widget.show()
            self.viewport.rwindow.Render()

    @pyqtSlot()
    def on_pbLOY_clicked(self):
        if self.editorModel.prop in self.editorModel.props:
            actor = self.editorModel.props[self.editorModel.prop]
            actor.mesh.rotate_y(-1, inplace=True)
            self.manipulator_widget.show()
            self.viewport.rwindow.Render()


    @pyqtSlot()
    def on_pbROX_clicked(self):
        if self.editorModel.prop in self.editorModel.props:
            actor = self.editorModel.props[self.editorModel.prop]
            actor.mesh.rotate_x(1, inplace=True)
            self.manipulator_widget.show()
            self.viewport.rwindow.Render()


    @pyqtSlot()
    def on_pbLOX_clicked(self):
        if self.editorModel.prop in self.editorModel.props:
            actor = self.editorModel.props[self.editorModel.prop]
            actor.mesh.rotate_x(-1, inplace=True)
            self.manipulator_widget.show()
            self.viewport.rwindow.Render()


    @pyqtSlot()
    def on_pbUP_clicked(self):
        if self.editorModel.prop in self.editorModel.props:
            actor = self.editorModel.props[self.editorModel.prop]
            actor.mesh.move(dx=0, dy=0, dz=self.dsbStep.value(), inplace=True)
            self.manipulator_widget.show()
            self.viewport.rwindow.Render()


    @pyqtSlot()
    def on_pbRIGHT_clicked(self):
        if self.editorModel.prop in self.editorModel.props:
            actor = self.editorModel.props[self.editorModel.prop]
            actor.mesh.move(dx=self.dsbStep.value(), dy=0, dz=0, inplace=True)
            self.manipulator_widget.show()
            self.viewport.rwindow.Render()


    @pyqtSlot()
    def on_pbDOWN_clicked(self):
        if self.editorModel.prop in self.editorModel.props:
            actor = self.editorModel.props[self.editorModel.prop]
            actor.mesh.move(dx=0, dy=0, dz=-self.dsbStep.value(), inplace=True)
            self.manipulator_widget.show()
            self.viewport.rwindow.Render()


    @pyqtSlot()
    def on_pbLEFT_clicked(self):
        if self.editorModel.prop in self.editorModel.props:
            actor = self.editorModel.props[self.editorModel.prop]
            actor.mesh.move(dx=-self.dsbStep.value(), dy=0, dz=0, inplace=True)
            self.manipulator_widget.show()
            self.viewport.rwindow.Render()    

    def updateManip(self):
        if not self.editorModel.prop:
            self.pbManipulator.setEnabled(False)
        else:
            self.pbManipulator.setEnabled(True)

        if self.pbManipulator.isChecked():
            self.on_pbManipulator_toggled(True)


    def on_pbPreview_pressed(self):
        log = open('C:/Users/Public/Documents/log_file.txt','a')
        log.write('Предпросмотр'+'\n')
        log.close()
        self.previewdialog.emit()


class CubeW(object):

    def __init__(self, interactor, prop, on_select, cuttools):
        self.interactor = interactor
        self.prop = prop
        self.on_select = on_select
        self.cuttools = cuttools

        self.widget = vtk.vtkBoxWidget()
        self.widget.SetInteractor(interactor)
        # self.widget.SetProp3D(self.prop)
        self.widget.PlaceWidget(self.prop.mesh.bounds)

        self.widget.GetFaceProperty().SetEdgeColor(get_color('blue'))
        self.widget.GetSelectedFaceProperty().SetEdgeColor(get_color('yellow'))

        self.widget.AddObserver(vtk.vtkCommand.InteractionEvent, self.event)

    @property
    def bounds(self):
        return self.prop.mesh.bounds

    @property
    def transform(self):
        trans = vtk.vtkTransform()
        self.widget.GetTransform(trans)
        return trans

    @property
    def scale(self):
        return self.transform.GetScale()

    @property
    def position(self):
        return self.transform.GetPosition()

    @property
    def orientation(self):
        return self.transform.GetOrientation()

    @property
    def width(self):
        return (self.bounds[1] - self.bounds[0]) * self.scale[0]

    @property
    def height(self):
        return (self.bounds[3] - self.bounds[2]) * self.scale[1]

    @property
    def depth(self):
        return (self.bounds[5] - self.bounds[4]) * self.scale[2]

    def event(self, caller=None, ev=None):
        self.on_select(self.as_planes())

        self.cuttools.lPosition_1.setText(str(self.position[0]))
        self.cuttools.lPosition_2.setText(str(self.position[1]))
        self.cuttools.lPosition_3.setText(str(self.position[2]))
        print('Cube position: {}'.format(self.position))

        self.cuttools.lOrientation_1.setText(str(self.orientation[0]))
        self.cuttools.lOrientation_2.setText(str(self.orientation[1]))
        self.cuttools.lOrientation_3.setText(str(self.orientation[2]))
        print('Cube orientation: {}'.format(self.orientation))

        self.cuttools.lScale_1.setText(str(self.scale[0]))
        self.cuttools.lScale_2.setText(str(self.scale[1]))
        self.cuttools.lScale_3.setText(str(self.scale[2]))
        print('Cube scale: {}'.format(self.scale))

    @property
    def renderer(self):
        return self.interactor.GetRenderWindow().GetRenderers().GetFirstRenderer()

    def show(self):
        self.widget.On()
        self.event()

    def hide(self):
        self.widget.Off()

    def as_polydata(self):
        poly_data = vtk.vtkPolyData()
        self.widget.GetPolyData(poly_data)
        return poly_data

    def as_planes(self):
        planes = vtk.vtkPlanes()
        self.widget.GetPlanes(planes)
        return planes


class PlaneW(object):

    class ImplicitPlaneInteractionCallback(object):
        """     """

        def __init__(self, hi=None, plane=None, interactor=None):
            """     """
            self.hi = hi
            self._plane = plane
            self._iren = interactor

        def __call__(self, caller=None, ev=None):
            if not self.hi.orig:
                return
            """     """
            if hasattr(caller, 'GetRepresentation'):
                rep = caller.GetRepresentation()
                if hasattr(rep, 'GetPlane') and self._plane:
                    rep.GetPlane(self._plane)

            # mesh = self.hi.orig.mesh
            # left, right = mesh.disect_by_plane(self._plane)
            # self.hi.renderer.RemoveActor(self.hi.precut_left)
            # self.hi.renderer.RemoveActor(self.hi.precut_right)
            # self.hi.precut_left = PolyActor(left,
            #                                 color='red',
            #                                 opacity=1.0)
            # self.hi.precut_right = PolyActor(right,
            #                                  color='green',
            #                                  opacity=1.0)
            # self.hi.renderer.AddActor(self.hi.precut_left)
            # self.hi.renderer.AddActor(self.hi.precut_right)

    def __init__(self, interactor):
        """     """

        self.editorModel = editorModel
        self.editorModel.propSelected.connect(self.event2)
        # self.editorModel.inverseUpdated.connect(self.event2)
        if self.editorModel.prop:
            self._iren = interactor
            self._bounds = self.orig.mesh.bounds
            center = self.orig.mesh.center
            if math.isnan(center[0]):
                center = ((self._bounds[0] + self._bounds[1]) / 2,
                          (self._bounds[2] + self._bounds[3]) / 2,
                          (self._bounds[4] + self._bounds[5]) / 2)
            self._plane = Plane(origin=center, normal=(1, 0, 0))
            self._callback = PlaneW.ImplicitPlaneInteractionCallback(self,
                                                                     self._plane,
                                                                     self._iren)

            # left, right = self.orig.mesh.disect_by_plane(self._plane)
            # self.precut_left = PolyActor(left,
            #                              color='red',
            #                              opacity=1.0)
            # self.precut_right = PolyActor(right,
            #                               color='green',
            #                               opacity=1.0)
            # self.renderer.AddActor(self.precut_left)
            # self.renderer.AddActor(self.precut_right)

            self.rep = vtk.vtkImplicitPlaneRepresentation()
            self.rep.SetPlaceFactor(1.25)
            print(self.orig.mesh.center)
            print(self._bounds)
            self.rep.PlaceWidget(self._bounds)
            self.rep.SetNormal(self._plane.GetNormal())
            self.rep.SetOrigin(self._plane.GetOrigin())
            self.rep.DrawOutlineOff()
            self.rep.DrawPlaneOn()

            self.widget = vtk.vtkImplicitPlaneWidget2()
            self.widget.SetInteractor(self._iren)
            self.widget.SetRepresentation(self.rep)
            self.widget.AddObserver(vtk.vtkCommand.InteractionEvent,
                                    self._callback)

    def _pos(self, value):
        origin = self._plane.GetOrigin()
        self._plane.SetOrigin(value, origin[1], origin[2])
        self.rep.SetOrigin(self._plane.GetOrigin())

    def event2(self):
        self._callback()
        self._iren.GetRenderWindow().Render()

    def show(self):
        self.widget.On()

    def hide(self):
        self.widget.Off()
        # self.renderer.RemoveActor(self.precut_left)
        # self.renderer.RemoveActor(self.precut_right)

    @property
    def renderer(self):
        return self._iren.GetRenderWindow().GetRenderers().GetFirstRenderer()

    @property
    def orig(self):
        orig = None
        if self.editorModel.prop in self.editorModel.props:
            orig = self.editorModel.props[self.editorModel.prop]
        return orig

    @property
    def plane(self):
        return self._plane


class PlaneW2(object):

    class ImplicitPlaneInteractionCallback(object):
        """     """

        def __init__(self, hi=None, plane=None, interactor=None):
            """     """
            self.hi = hi
            self._plane = plane
            self._iren = interactor

        def __call__(self, caller=None, ev=None):
            if not self.hi.orig:
                return
            """     """
            if hasattr(caller, 'GetRepresentation'):
                rep = caller.GetRepresentation()
                if hasattr(rep, 'GetPlane') and self._plane:
                    rep.GetPlane(self._plane)

            mesh = self.hi.orig.mesh
            left, right = mesh.disect_by_plane(self._plane)
            self.hi.renderer.RemoveActor(self.hi.precut_left)
            self.hi.renderer.RemoveActor(self.hi.precut_right)
            self.hi.precut_left = PolyActor(left,
                                            color='red',
                                            opacity=1.0)
            self.hi.precut_right = PolyActor(right,
                                             color='green',
                                             opacity=1.0)
            self.hi.renderer.AddActor(self.hi.precut_left)
            self.hi.renderer.AddActor(self.hi.precut_right)

    def __init__(self, interactor):
        """     """

        self.editorModel = editorModel
        self.editorModel.propSelected.connect(self.event2)
        # self.editorModel.inverseUpdated.connect(self.event2)
        if self.editorModel.prop:
            self._iren = interactor
            self._bounds = self.orig.mesh.bounds
            center = self.orig.mesh.center
            if math.isnan(center[0]):
                center = ((self._bounds[0] + self._bounds[1]) / 2,
                          (self._bounds[2] + self._bounds[3]) / 2,
                          (self._bounds[4] + self._bounds[5]) / 2)
            self._plane = Plane(origin=center, normal=(1, 0, 0))
            self._callback = PlaneW.ImplicitPlaneInteractionCallback(self,
                                                                     self._plane,
                                                                     self._iren)

            left, right = self.orig.mesh.disect_by_plane(self._plane)
            self.precut_left = PolyActor(left,
                                         color='red',
                                         opacity=1.0)
            self.precut_right = PolyActor(right,
                                          color='green',
                                          opacity=1.0)
            self.renderer.AddActor(self.precut_left)
            self.renderer.AddActor(self.precut_right)

            self.rep = vtk.vtkImplicitPlaneRepresentation()
            self.rep.SetPlaceFactor(1.25)
            print(self.orig.mesh.center)
            print(self._bounds)
            self.rep.PlaceWidget(self._bounds)
            self.rep.SetNormal(self._plane.GetNormal())
            self.rep.SetOrigin(self._plane.GetOrigin())
            self.rep.DrawOutlineOff()
            self.rep.DrawPlaneOn()

            self.widget = vtk.vtkImplicitPlaneWidget2()
            self.widget.SetInteractor(self._iren)
            self.widget.SetRepresentation(self.rep)
            self.widget.AddObserver(vtk.vtkCommand.InteractionEvent,
                                    self._callback)

    def _pos(self, value):
        origin = self._plane.GetOrigin()
        self._plane.SetOrigin(value, origin[1], origin[2])
        self.rep.SetOrigin(self._plane.GetOrigin())

    def event2(self):
        self._callback()
        self._iren.GetRenderWindow().Render()

    def show(self):
        self.widget.On()

    def hide(self):
        self.widget.Off()
        self.renderer.RemoveActor(self.precut_left)
        self.renderer.RemoveActor(self.precut_right)

    @property
    def renderer(self):
        return self._iren.GetRenderWindow().GetRenderers().GetFirstRenderer()

    @property
    def orig(self):
        orig = None
        if self.editorModel.prop in self.editorModel.props:
            orig = self.editorModel.props[self.editorModel.prop]
        return orig

    @property
    def plane(self):
        return self._plane

