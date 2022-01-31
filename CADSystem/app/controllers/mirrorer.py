import vtk
import time

from PyQt5.QtCore import pyqtSlot, Qt, QTimer, QEventLoop
from PyQt5.QtWidgets import QWidget, QFileDialog, QProgressDialog, QErrorMessage

from libcore.qt import Viewport
from libcore.widget import PlaneSelector, CubeManipulator
from libcore.geometry import Plane, point_distance
from libcore.topology import delete_cells, extract_cells_using_points
from libcore.display import PolyActor
from libcore.mesh import Mesh

from ..models.look import lookModel
from ..models.mirrorer import mirrorerModel
from ..models.implantor import implantorModel
from ..models.stage import stageModel

from ..views.mirrorer_ui import Ui_Mirrorer


def doGenerate(doneFunc, setValue):
    for x2 in range(25):
        loop = QEventLoop()
        QTimer.singleShot(1000, loop.quit)
        loop.exec_()
        setValue(x2 + 1)
    doneFunc()


class Mirrorer(QWidget, Ui_Mirrorer):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
        self.viewport = Viewport()
        self.viewport.istyle = vtk.vtkInteractorStyleTrackballCamera()
        self.viewport.interactor.Initialize()
        self.layout.addWidget(self.viewport)

        self.wImport.setVisible(False)

        self.lookModel = lookModel
        self.lookModel.lookUpdated.connect(self.updateLook)

        self.mirrorerModel = mirrorerModel
        self.mirrorerModel.meshLoaded.connect(self.loadMesh)

        self.implantorModel = implantorModel

        self.stageModel = stageModel

    @pyqtSlot(tuple)
    def updateLook(self, look):
        self.viewport.look_from(look)

    @pyqtSlot()
    def updateRender(self):
        self.viewport.rwindow.Render()

    def loadMesh(self):
        if self.mirrorerModel.mesh:
            if hasattr(self, 'actor'):
                self.viewport.remove_prop(self.actor)

            mesh = self.mirrorerModel.mesh
            self.actor = PolyActor(mesh,
                                   color='white',
                                   opacity=self.hsMesh.value() / 100)
            self.viewport.add_prop(self.actor)

            if self.pbMirrorer.isChecked():
                self.plane = PlaneSelector(self.viewport.interactor,
                                           Plane.XZ(origin=mesh.center),
                                           mesh.bounds)
                self.plane.widget.AddObserver(vtk.vtkCommand.EndInteractionEvent,
                                              self._callback)
                self.plane.show()
                self.viewport.reset_view()
                self.plane._callback(None, None)
                self._callback(None, None)

    def on_pbNetwork_pressed(self):
        log = open('C:/Users/Public/Documents/log_file.txt','a')
        log.write('Поиск недостающего объема'+'\n')
        log.close()
        if self.pbManipulator.isChecked():
            self.pbManipulator.setChecked(Qt.Unchecked)
        self.on_pbMirrorer_toggled(False)
        if hasattr(self, 'plane'):
            self.plane.hide()
            del self.plane
        if hasattr(self, 'precut'):
            self.viewport.remove_prop(self.precut)
            del self.precut
        if hasattr(self, 'precut2'):
            del self.precut2
        if self.pbMirrorer.isChecked():
            self.pbMirrorer.setChecked(Qt.Unchecked)

        self.updateRender()

        progress = QProgressDialog('Поиск недостающего объема',
                                   '', 0, 25, self)
        progress.resize(300, 100)
        progress.setWindowTitle("Поиск недостающего объема...")
        progress.setWindowModality(Qt.WindowModal)
        progress.setValue(0)
        progress.show()
        doGenerate(self.show_implant, progress.setValue)

    def show_implant(self):
        if hasattr(self.stageModel, 'name'):
            result = Mesh('pet-implant.stl')
            self.result = PolyActor(mesh=result,
                                    color='red')
            self.viewport.add_prop(self.result)
        else:
            error_dialog = QErrorMessage(self)
            error_dialog.showMessage('Ошибка поиска недостающего объема')
            self.on_pbMirrorer_toggled(True)

    def on_pbImport_pressed(self):
        log = open('C:/Users/Public/Documents/log_file.txt','a')
        log.write('Загрузка шаблона'+'\n')
        log.close()
        if self.pbManipulator.isChecked():
            self.pbManipulator.setChecked(Qt.Unchecked)
        self.on_pbMirrorer_toggled(False)
        if hasattr(self, 'plane'):
            self.plane.hide()
            del self.plane
        if hasattr(self, 'precut'):
            self.viewport.remove_prop(self.precut)
            del self.precut
        if hasattr(self, 'precut2'):
            del self.precut2
        if self.pbMirrorer.isChecked():
            self.pbMirrorer.setChecked(Qt.Unchecked)

        file_name, _ = QFileDialog.getOpenFileName(self,
                                                   "Открыть STL",
                                                   "",
                                                   "Файлы STL (*.stl)")
        if file_name:
            mesh = Mesh(file_name)
            self.precut = PolyActor(
                mesh, color='green', opacity=self.hsImplant.value() / 100)
            self.manipulator = CubeManipulator(self.viewport.interactor,
                                               self.precut)
            self.manipulator.show()
            self.viewport.add_prop(self.precut)
            self.viewport.reset_view()

    def on_pushButtonFlipX_pressed(self):
        log = open('C:/Users/Public/Documents/log_file.txt','a')
        log.write('Зеркальное отображение относительно Х'+'\n')
        log.close()
        self.precut.mesh.reflect(plane='x', inplace=True)
        self.manipulator.show()
        self.updateRender()

    def on_pushButtonFlipY_pressed(self):
        log = open('C:/Users/Public/Documents/log_file.txt','a')
        log.write('Зеркальное отображение относительно Y'+'\n')
        log.close()
        self.precut.mesh.reflect(plane='y', inplace=True)
        self.manipulator.show()
        self.updateRender()

    def on_pushButtonFlipZ_pressed(self):
        log = open('C:/Users/Public/Documents/log_file.txt','a')
        log.write('Зеркальное отображение относительно Z'+'\n')
        log.close()
        self.precut.mesh.reflect(plane='z', inplace=True)
        self.manipulator.show()
        self.updateRender()

    def on_tbMinus_pressed(self):
        log = open('C:/Users/Public/Documents/log_file.txt','a')
        log.write('Уменьшение масштаба'+'\n')
        log.close()
        self.precut.mesh.scale(sx=0.95, sy=0.95, sz=0.95, inplace=True)
        self.manipulator.show()
        self.updateRender()

    def on_tbPlus_pressed(self):
        log = open('C:/Users/Public/Documents/log_file.txt','a')
        log.write('Увеличение масштаба'+'\n')
        log.close()
        self.precut.mesh.scale(sx=1.05, sy=1.05, sz=1.05, inplace=True)
        self.manipulator.show()
        self.updateRender()

    def on_pbMirrorer_toggled(self, toggle):
        self.wImport.setHidden(toggle)
        self.wMirrorer.setVisible(toggle)
        if toggle:
            if hasattr(self, 'manipulator'):
                self.manipulator.hide()
                del self.manipulator
            self.loadMesh()

    def on_pbManipulator_toggled(self, toggle):
        if hasattr(self, 'manipulator'):
            self.precut.mesh = self.manipulator.mesh
            self.manipulator.hide()
            self._callback(None, None)
            del self.manipulator

        self.plane.show()

        if toggle:
            self.plane.hide()
            self.manipulator = CubeManipulator(self.viewport.interactor,
                                               self.precut)
            self.manipulator.show()

        self.updateRender()

    def _callback(self, caller, ev):
        if hasattr(self, 'precut'):
            self.viewport.remove_prop(self.precut)

        left, right = self.actor.mesh.disect_by_plane(self.plane.plane)

        if self.rbLeft.isChecked():
            precut = right
            self.precut2 = left
        else:
            precut = left
            self.precut2 = right

        precut.reflect(plane='x', inplace=True)

        if self.rbLeft.isChecked():
            delta = self.actor.mesh.max_x - precut.max_x
        else:
            delta = self.actor.mesh.min_x - precut.min_x

        precut.move(dx=delta, dy=0, dz=0, inplace=True)

        # precut.close_mesh(inplace=True)
        self.precut = PolyActor(precut,
                                color='green',
                                opacity=self.hsImplant.value() / 100)
        self.viewport.add_prop(self.precut)

    def on_pbFind_pressed(self):
        log = open('C:/Users/Public/Documents/log_file.txt','a')
        log.write('Поиск недостающего объема'+'\n')
        log.close()
        if hasattr(self, 'result'):
            self.viewport.remove_prop(self.result)

        if hasattr(self, 'precut'):
            if hasattr(self, 'manipulator'):
                self.viewport.remove_prop(self.precut)
                self.precut = PolyActor(self.manipulator.mesh,
                                        color='green',
                                        opacity=self.hsImplant.value() / 100)
                self.viewport.add_prop(self.precut)
            if hasattr(self, 'precut2'):
                mesh = self.precut2
            else:
                mesh = self.actor.mesh
            good_points_indexes = []
            for idx, pt in enumerate(self.precut.mesh.points):
                closest_idx = mesh.find_closest_point(point=pt)
                closest_pt = mesh.points[closest_idx]
                distance = point_distance(pt, closest_pt)
                if distance > self.dsbDistance.value():
                    good_points_indexes.append(idx)

            result = extract_cells_using_points(self.precut.mesh,
                                                good_points_indexes)
            result.extract_largest(inplace=True)
            self.result = PolyActor(mesh=result,
                                    color='red')
            self.viewport.add_prop(self.result)

    def on_pbNext_pressed(self):
        log = open('C:/Users/Public/Documents/log_file.txt','a')
        log.write('Переход на следующий этап'+'\n')
        log.close()
        mesh = self.actor.mesh
        if hasattr(self, 'precut'):
            implant = self.precut.mesh
        if hasattr(self, 'result'):
            implant = self.result.mesh
        self.implantorModel.addProp('implant', PolyActor(implant))
        self.implantorModel.addProp('mesh', PolyActor(mesh))
        self.stageModel.stage = 5

    def on_buttonGroup_buttonClicked(self, btn):
        self._callback(None, None)

    def on_pbSave_pressed(self):
        log = open('C:/Users/Public/Documents/log_file.txt','a')
        log.write('Сохранение STL'+'\n')
        log.close()
        file_name, _ = QFileDialog.getSaveFileName(self,
                                                   "Сохранить STL",
                                                   "",
                                                   "Файлы STL (*.stl)")
        if file_name:
            if hasattr(self, 'result'):
                self.result.mesh.save(file_name)
            else:
                self.precut.mesh.save(file_name)
            print(file_name)

    def on_hsMesh_valueChanged(self, opacity):
        if hasattr(self, 'actor'):
            self.actor.opacity = opacity / 100
            self.updateRender()

    def on_hsImplant_valueChanged(self, opacity):
        if hasattr(self, 'precut'):
            self.precut.opacity = opacity / 100
            self.updateRender()
