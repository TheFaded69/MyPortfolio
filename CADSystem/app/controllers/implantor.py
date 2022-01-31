import vtk
import math
import numpy as np

from PyQt5.QtCore import pyqtSlot, pyqtSignal, QObject, Qt
from PyQt5.QtWidgets import QWidget, QFileDialog

from libcore.display import PolyActor
from libcore.qt import Viewport
from libcore.interact import StyleDrawPolygon3, StyleActorSelection, StyleRubberBand2D, CircleSelection
from libcore.color import get_color
from libcore.widget import Label, CubeManipulator, SphereWidget, ArrowProbe, PlaneSelector
from libcore.geometry import Plane, vec_add, vec_normalize, vec_norm, point_distance
from libcore.topology import mesh_inflate, mesh_deflate, delete_cells, extract_cells_using_points
from libcore.mesh import Mesh, square_warp
from libcore.topology import delete_cells
from libcore.topology import face_for_point

from ..models.implantor import implantorModel
from ..models.look import lookModel
from ..models.mirrorer import mirrorerModel
from ..models.stage import stageModel
from ..models.mounter import mounterModel

from ..views.implantor_ui import Ui_Implantor


class Implantor(QWidget, Ui_Implantor):
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

        self._prop = None

        self.wFlate.setHidden(True)
        self.wDeformation.setVisible(False)
        self.pbFlate.setVisible(False)

        self.viewport = Viewport()
        self.viewport.istyle = vtk.vtkInteractorStyleTrackballCamera()
        self.viewport.interactor.Initialize()
        self.layout.addWidget(self.viewport)
        self.viewport.interactor.AddObserver(vtk.vtkCommand.CharEvent,
                                             self.callback)

        self.selection_actor = None
        self.selection_indexes = []
        self.mesh = None
        self.arrow = None

        self.implantorModel = implantorModel
        self.implantorModel.propSelected.connect(self.updateRender)
        self.implantorModel.propSelected.connect(self.updateManip)
        self.implantorModel.propsUpdated.connect(self.updateProps)
        self.implantorModel.cutterPolyline.toolUpdated.connect(self.updateTool)
        self.implantorModel.cutterRect.toolUpdated.connect(self.updateTool)
        self.implantorModel.cutterCube.toolUpdated.connect(self.updateTool)
        self.implantorModel.cutterCircle.toolUpdated.connect(self.updateTool)
        self.implantorModel.cutterCircle.cutUpdated.connect(self.cutCircle)
        self.implantorModel.cutterSphere.toolUpdated.connect(self.updateTool)
        self.implantorModel.cutterSphere.cutUpdated.connect(self.cutSphere)
        self.implantorModel.cutterPlane.toolUpdated.connect(self.updateTool)
        self.implantorModel.cutterPlane.cutUpdated.connect(self.cutPlane)
        self.implantorModel.splitter.toolUpdated.connect(self.updateTool)

        self.implantorModel.crossSectionUpdated.connect(
            self.updateCrossSectionTool)
        self.implantorModel.ruler3DUpdated.connect(self.updateRuler3DTool)

        self.lookModel = lookModel
        self.lookModel.lookUpdated.connect(self.updateLook)

        self.mirrorerModel = mirrorerModel

        self.stageModel = stageModel

        self.cuttools.setModel(implantorModel)
        self.meshtools.setModel(implantorModel)
        self.props.setModel(implantorModel)

        self.mounterModel = mounterModel

    def updateCrossSectionTool(self, toggle):
        if toggle:
            self.implantorModel.cutterPolyline.toggle = False
            self.implantorModel.cutterRect.toggle = False
            self.implantorModel.cutterCircle.toggle = False
            self.implantorModel.cutterCube.toggle = False
            self.implantorModel.cutterSphere.toggle = False
            self.implantorModel.cutterPlane.toggle = False

            for prop in self.implantorModel.props:
                self.implantorModel.props[prop].opacity = 0.2

            a = list(self.implantorModel.props.keys())
            while a:
                i = a.pop(0)
                for j in a:
                    mesh = self.implantorModel.props[j].mesh.slice_by_mesh(
                        self.implantorModel.props[i].mesh)
                    actor = PolyActor(mesh=mesh,
                                      color=self.implantorModel.props[j].color,
                                      render_lines_as_tubes=True,
                                      line_width=5.0,
                                      opacity=1.0)
                    print(actor)
                    self.viewport.renderer.AddActor(actor)
                    self.crossSectionActors.append(actor)
        else:
            for prop in self.implantorModel.props:
                self.implantorModel.props[prop].opacity = 1.0
            while self.crossSectionActors:
                prop = self.crossSectionActors.pop(0)
                self.viewport.renderer.RemoveActor(prop)

        self.viewport.rwindow.Render()

    def updateRuler3DTool(self, toggle):
        if toggle:
            self.implantorModel.cutterPolyline.toggle = False
            self.implantorModel.cutterRect.toggle = False
            self.implantorModel.cutterCircle.toggle = False
            self.implantorModel.cutterCube.toggle = False
            self.implantorModel.cutterSphere.toggle = False
            self.implantorModel.cutterPlane.toggle = False

            self.widget_ruler3d = vtk.vtkLineWidget2()
            self.widget_ruler3d.SetInteractor(self.viewport.interactor)
            self.widget_ruler3d.CreateDefaultRepresentation()
            rep = self.widget_ruler3d.GetLineRepresentation()
            rep.SetPoint2WorldPosition(np.array(rep.GetPoint2WorldPosition()) * 50)
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
        self.meshtools.lRuler3D.setText('Длина: {:-f} мм'.format(distance))

    def on_pbFlate_toggled(self, toggle):
        self.wFlate.setVisible(toggle)
        if toggle:
            self.on_pbDeformation_toggled(False)
            if not self.pbFlate.isChecked():
                self.pbFlate.setChecked(Qt.Checked)

            self.sphere_widget = SphereWidget(
                interactor=self.viewport.interactor)
            self.sphere_widget.show()
        else:
            if self.pbFlate.isChecked():
                self.pbFlate.setChecked(Qt.Unchecked)

            if hasattr(self, 'sphere_widget'):
                self.sphere_widget.hide()
                del self.sphere_widget

    def on_pbFlateApply_pressed(self):
        log = open('C:/Users/Public/Documents/log_file.txt','a')
        log.write('Применить вытягивание'+'\n')
        log.close()
        if self.implantorModel.prop:
            actor = self.implantorModel.props[self.implantorModel.prop]
            if self.rbInflate.isChecked():
                actor.mesh = mesh_inflate(mesh=actor.mesh,
                                          center=self.sphere_widget.center,
                                          radius=self.sphere_widget.radius)
            else:
                actor.mesh = mesh_deflate(mesh=actor.mesh,
                                          center=self.sphere_widget.center,
                                          radius=self.sphere_widget.radius)

        self.updateRender()

    def on_pbDeformation_toggled(self, toggle):
        self.rbTool.setEnabled(toggle)
        self.wDeformation.setVisible(toggle)
        if toggle:
            self.on_pbManipulator_toggled(False)
            self.on_pbFlate_toggled(False)
            if not self.pbDeformation.isChecked():
                self.pbDeformation.setChecked(Qt.Checked)
            self.on_rbTool_toggled(True)
        else:
            if self.pbDeformation.isChecked():
                self.pbDeformation.setChecked(Qt.Unchecked)
            if self.selection_actor:
                self.viewport.remove_prop(self.selection_actor)
                self.selection_actor = None
            if self.arrow:
                self.arrow.hide()
                self.arrow = None
            self.on_rbCamera_toggled(True)
        self.updateRender()

    def on_pbReverseSense_pressed(self):
        log = open('C:/Users/Public/Documents/log_file.txt','a')
        log.write('Переворот нормалей для вытягивания'+'\n')
        log.close()
        self.mesh.reverse_sense(inplace=True)
        self.mesh.compute_normals()
        self.on_rbTool_toggled(True)

    def on_pbDeformationApply_pressed(self):
        log = open('C:/Users/Public/Documents/log_file.txt','a')
        log.write('Применить деформацию'+'\n')
        log.close()
        if self.arrow:
            square_warp(self.mesh,
                        self.selection_indexes,
                        center=self.arrow.point1,
                        direction=self.arrow.direction,
                        length=self.arrow.length)

            self.on_pbDeformation_toggled(False)
            self.on_pbDeformation_toggled(True)

    def on_selected(self, center, indexes):
        if self.implantorModel.prop in self.implantorModel.props:
            self.arrow = ArrowProbe(interactor=self.viewport.interactor,
                                    origin=center,
                                    on_changed=None)
            self.arrow.point2 = list(np.array(
                center) + 10 * self.mesh.normals[self.mesh.find_closest_point(center)])
            self.arrow.show()

            # Выключаем режим
            self.selection_actor = self.viewport.istyle.selection_actor
            self.selection_indexes = self.viewport.istyle.selection_indexes
            self.on_rbCamera_toggled(True)

            self.updateRender()

    def callback(self, caller, event):
        if self.viewport.interactor.GetKeySym() == 'Escape':
            if self.rbTool.isChecked():
                self.on_rbCamera_toggled(True)
            elif self.rbTool.isEnabled():
                self.on_rbTool_toggled(True)

    @pyqtSlot()
    def updateRender(self):
        self.viewport.rwindow.Render()

    def updateManip(self):
        if not self.implantorModel.prop:
            self.pbManipulator.setEnabled(False)
            self.pbDeformation.setEnabled(False)
        else:
            self.pbManipulator.setEnabled(True)
            self.pbDeformation.setEnabled(True)

        if self.pbManipulator.isChecked():
            self.on_pbManipulator_toggled(True)

    @pyqtSlot()
    def updateProps(self):
        for prop in self.viewport.actors():
            self.viewport.remove_prop(prop)
        if self._tool_cube:
            self._tool_cube.hide()
            self._tool_cube.show()
        if hasattr(self, 'manipulator_widget'):
            if self.pbManipulator.isChecked():
                self.manipulator_widget.hide()
                self.manipulator_widget.show()

        self._prop = self.implantorModel.prop

        if self.implantorModel.cutterCircle.toggle:
            if self.implantorModel.prop in self.implantorModel.props:
                mesh = self.implantorModel.props[self.implantorModel.prop].mesh
                self.viewport.istyle.set_mesh(mesh)

        self.viewport.add_props(self.implantorModel.props.values())

    @pyqtSlot(QObject)
    def updateTool(self, tool):
        self.on_pbManipulator_toggled(False)
        self.on_pbFlate_toggled(False)
        self.on_pbDeformation_toggled(False)

        if tool.toggle:
            self.meshtools.on_pbCrossSection_toggled(False)

            self.viewport.renderer.RemoveActor(self._tool_precut)
            if hasattr(tool, 'precut'):
                self._tool_precut = tool.precut
            if hasattr(tool, 'parts'):
                for part in self._tool_parts:
                    self.viewport.remove_prop(part)
                self._tool_parts = tool.parts
            if self.pbDeformation.isChecked():
                self.on_pbDeformation_toggled(False)
        else:
            self.on_rbCamera_toggled(True)
            self.rbTool.setEnabled(False)

            if self._tool_cube:
                self._tool_cube.hide()
                self._tool_cube = None
                if self.implantorModel.prop in self.implantorModel.props:
                    prop = self.implantorModel.props[self.implantorModel.prop]
                    prop.opacity = 1.0
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
                if self.implantorModel.prop in self.implantorModel.props:
                    self.viewport.add_prop(self.implantorModel.props[
                        self.implantorModel.prop])

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
                prop = self.implantorModel.props[self.implantorModel.prop]
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
            #     prop = self.implantorModel.props[self.implantorModel.prop]
            #     self._tool_cube = CubeW(interactor=self.viewport.interactor,
            #                             prop=prop,
            #                             on_select=tool.update,
            #                             cuttools=self.cuttools)
            #     self._tool_cube.show()
        elif tool.name == 'plane':
            # self.viewport.remove_prop(self.implantorModel.props[
            #                           self.implantorModel.prop])
            # self.viewport.add_props(tool.parts)
            if not self._tool_plane:
                # prop = self.implantorModel.props[self.implantorModel.prop]
                # self._tool_plane = PlaneW(interactor=self.viewport.interactor,
                #                           prop=prop,
                #                           on_select=tool.update)
                # self.viewport.remove_prop(self.implantorModel.props[
                #                           self.implantorModel.prop])
                self._tool_plane = PlaneW(interactor=self.viewport.interactor)
                self._tool_plane.show()

        elif tool.name == 'splitter':
            if self.implantorModel.prop in self.implantorModel.props:
                prop = self.implantorModel.props[self.implantorModel.prop]
                self.viewport.remove_prop(prop)
                self.viewport.add_props(tool.parts)

        self.updateRender()

    def cutPlane(self, tool):
        if self._tool_plane:

            left, right = self._tool_plane.orig.mesh.disect_by_plane(
                self._tool_plane._plane)

            if self.implantorModel.cutterPlane.close_mesh:
                left.fill_holes(inplace=True)
                right.fill_holes(inplace=True)

            self.implantorModel.addProp(self.implantorModel.prop + '.l',
                                        PolyActor(left))
            self.implantorModel.addProp(self.implantorModel.prop + '.r',
                                        PolyActor(right))
            self.implantorModel.delProp()
            self.updateProps()
            self.updateTool(self.implantorModel.cutterPlane)
            # self.implantorModel.cutterPlane.toggle = False

    def cutSphere(self, tool):
        if self._tool_sphere:
            if self.implantorModel.prop in self.implantorModel.props:
                prop = self.implantorModel.props[self.implantorModel.prop]
                self.implantorModel.props[self.implantorModel.prop] = PolyActor(prop.mesh.clip_by_mesh(self._tool_sphere.mesh,
                                                                                                       inverse=tool.inverse),
                                                                                color=prop.color)
                self.updateProps()

                self.viewport.renderer.AddActor(self.sphere_actor)
                self._tool_sphere = CubeManipulator(interactor=self.viewport.interactor,
                                                    actor=self.sphere_actor)
                self._tool_sphere.show()

    def cutCircle(self, tool):
        if self.implantorModel.prop in self.implantorModel.props:
            prop = self.implantorModel.props[self.implantorModel.prop]

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
            self.rbCamera.setChecked(Qt.Checked)
            self.viewport.istyle = vtk.vtkInteractorStyleTrackballCamera()

    def on_rbTool_toggled(self, toggle):

        if toggle:
            self.rbTool.setChecked(True)
            cutterPolyline = self.implantorModel.cutterPolyline
            cutterRect = self.implantorModel.cutterRect
            cutterCircle = self.implantorModel.cutterCircle
            if cutterPolyline.toggle:
                self.viewport.istyle = StyleDrawPolygon3(interactor=self.viewport.interactor,
                                                         on_select=cutterPolyline.update)
            if cutterRect.toggle:
                self.viewport.istyle = StyleRubberBand2D(
                    on_selection=cutterRect.update)
            if cutterCircle.toggle:
                self.viewport.istyle = CircleSelection(interactor=self.viewport.interactor,
                                                       on_selected=None)
                if self.implantorModel.prop in self.implantorModel.props:
                    mesh = self.implantorModel.props[
                        self.implantorModel.prop].mesh
                    self.viewport.istyle.set_mesh(mesh)
            if self.pbDeformation.isChecked():
                if self.arrow:
                    self.arrow.hide()
                    self.arrow = None
                if self.selection_actor:
                    self.viewport.remove_prop(self.selection_actor)
                    self.selection_actor = None
                if self.implantorModel.prop in self.implantorModel.props:
                    props = self.implantorModel.props
                    self.mesh = props[self.implantorModel.prop].mesh
                    if hasattr(self.mesh, 'normals'):
                        if self.mesh.normals is None:
                            # self.mesh.reverse_sense(inplace=True)
                            self.mesh.compute_normals()
                    else:
                        # self.mesh.reverse_sense(inplace=True)
                        self.mesh.compute_normals()

                    self.viewport.istyle = CircleSelection(interactor=self.viewport.interactor,
                                                           on_selected=self.on_selected)
                    self.viewport.istyle.set_mesh(self.mesh)
                    self.updateRender()

    def on_pbNext_pressed(self):
        # if 'mesh' in self.implantorModel.props:
        #     self.mounterModel.mesh = self.implantorModel.props['mesh'].mesh

        mesh = None
        meshes = []
        for prop in self.implantorModel.props:
            if (prop[:4] == 'mesh') and mesh == None:
                mesh = self.implantorModel.props[prop].mesh
            else:
                meshes.append(self.implantorModel.props[prop].mesh)
        self.mounterModel.mesh = mesh
        self.mounterModel.implant = Mesh.from_meshes(meshes)

        # if 'implant' in self.implantorModel.props:
        #     self.mounterModel.implant = self.implantorModel.props['implant'].mesh

        self.stageModel.stage = 6

    def on_pbPlaneXY_toggled(self, toggle):
        if toggle:
            if self.implantorModel.prop in self.implantorModel.props:
                mesh = self.implantorModel.props[self.implantorModel.prop].mesh
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
        if toggle:
            if self.implantorModel.prop in self.implantorModel.props:
                mesh = self.implantorModel.props[self.implantorModel.prop].mesh
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
        if toggle:
            if self.implantorModel.prop in self.implantorModel.props:
                mesh = self.implantorModel.props[self.implantorModel.prop].mesh
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
        if hasattr(self, 'manipulator_widget'):
            if self._prop in self.implantorModel.props:
                self.implantorModel.reProp(self._prop,
                                           self.manipulator_widget.mesh)
            self.manipulator_widget.hide()
            del self.manipulator_widget

        if self.implantorModel.prop in self.implantorModel.props:
            actor = self.implantorModel.props[self.implantorModel.prop]
            self._prop = self.implantorModel.prop

        if toggle:
            self.on_pbDeformation_toggled(False)
            if hasattr(self, 'sphere_widget'):
                self.on_pbFlate_toggled(False)
            if self.implantorModel.prop in self.implantorModel.props:
                actor = self.implantorModel.props[self.implantorModel.prop]
                self._prop = self.implantorModel.prop
                self.manipulator_widget = CubeManipulator(self.viewport.interactor,
                                                          actor)
                self.manipulator_widget.show()
            if not self.pbManipulator.isChecked():
                self.pbManipulator.setChecked(Qt.Checked)
        else:
            if self.pbManipulator.isChecked():
                self.pbManipulator.setChecked(Qt.Unchecked)

    def on_pbSphere2_pressed(self):
        mesh = Mesh.sphere(center=(30, 0, 0),
                           radius=20.0,
                           resolution_theta=51,
                           resolution_phi=51)
        actor = PolyActor(mesh)
        prop = self.implantorModel.addProp('головка', actor)

        self.implantorModel.prop = prop
        self.on_pbManipulator_toggled(True)

    def on_pbCube2_pressed(self):
        mesh = Mesh.cube(width=30.0,
                         height=30.0,
                         depth=30.0)
        actor = PolyActor(mesh)
        prop = self.implantorModel.addProp('cube', actor)

        self.implantorModel.prop = prop
        self.on_pbManipulator_toggled(True)

    def on_pbTorus_pressed(self):
        mesh = Mesh.torus(crossection_radius=10,
                          ring_radius=20,
                          resolution_u=51,
                          resolution_v=51,
                          resolution_w=51)
        actor = PolyActor(mesh)
        prop = self.implantorModel.addProp('torus', actor)

        self.implantorModel.prop = prop
        self.on_pbManipulator_toggled(True)

    def on_pbCone_pressed(self):
        mesh = Mesh.cone(radius=10.0,
                         resolution=50,
                         height=30.0,
                         tesselation_level=2)
        actor = PolyActor(mesh)
        prop = self.implantorModel.addProp('cone', actor)

        self.implantorModel.prop = prop
        self.on_pbManipulator_toggled(True)

    def on_pbCylinder_pressed(self):
        mesh = Mesh.cylinder(center=(40.0, 0.0, 0.0),
                             radius=10.0,
                             height=50.0,
                             resolution=50,
                             capping=True,
                             tesselation_level=2)
        actor = PolyActor(mesh)
        prop = self.implantorModel.addProp('ножка', actor)

        self.implantorModel.prop = prop
        self.on_pbManipulator_toggled(True)

    # def on_pbTetrahedra_pressed(self):
    #     mesh = Mesh.tetrahedra(tesselation_level=2)
    #     actor = PolyActor(mesh)
    #     prop = self.implantorModel.addProp('tetrahedra', actor)

    #     self.implantorModel.prop = prop
    #     self.on_pbManipulator_toggled(True)

    # def on_pbOctahedron_pressed(self):
    #     mesh = Mesh.tetrahedra(tesselation_level=2)
    #     actor = PolyActor(mesh)
    #     prop = self.implantorModel.addProp('octahedron', actor)

    #     self.implantorModel.prop = prop
    #     self.on_pbManipulator_toggled(True)

    @pyqtSlot()
    def on_pbOpenSTL_pressed(self):
        file_name, _ = QFileDialog.getOpenFileName(self,
                                                   "Открыть STL",
                                                   "",
                                                   "Файлы STL (*.stl)")
        if file_name:
            mesh = Mesh(file_name)
            self.implantorModel.addProp('implant', PolyActor(mesh))

    def on_pbPreview_pressed(self):
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

        self.implantorModel = implantorModel
        self.implantorModel.propSelected.connect(self.event2)
        # self.implantorModel.inverseUpdated.connect(self.event2)
        if self.implantorModel.prop:
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
        if self.implantorModel.prop in self.implantorModel.props:
            orig = self.implantorModel.props[self.implantorModel.prop]
        return orig

    @property
    def plane(self):
        return self._plane


class Widget(object):
    pass


class TransformSelector(Widget):

    def __init__(self, interactor, actor):
        self._transform = vtk.vtkTransform()
        self._interactor = interactor
        self._actor = actor

        self.widget = vtk.vtkAffineWidget()
        self.widget.SetInteractor(self._interactor)
        self.widget.CreateDefaultRepresentation()
        # self.widget.GetAffineRepresentation()
        rep = self.widget.GetAffineRepresentation()
        # prop = rep.GetProperty()
        # prop.SetLineWidth(3)
        # prop.SetColor(get_color('white'))
        rep.DragableOff()
        # rep.SetBoxWidth(2)
        rep.GetProperty().SetColor(0.0, 0.0, 0.0)
        rep.GetProperty().SetLineWidth(1.5)
        # rep.SetAxesWidth(3)

        self.widget.GetRepresentation().PlaceWidget(actor.GetBounds())
        self.widget.AddObserver(
            vtk.vtkCommand.InteractionEvent, self._callback)
        self.widget.AddObserver(
            vtk.vtkCommand.EndInteractionEvent, self._callback)

    def _callback(self, caller, event):
        self.widget.GetAffineRepresentation().GetTransform(self._transform)
        self._actor.SetUserTransform(self._transform)

    def show(self):
        self.widget.On()

    def hide(self):
        self.widget.Off()
