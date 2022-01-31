from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QWidget, QAbstractButton, QButtonGroup

from ..views.cuttools_ui import Ui_CutTools

from ..models.editor import EditorModel, editorModel


class CutTools(QWidget, Ui_CutTools):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)

        self.wPolyline.setVisible(False)
        self.wRect.setVisible(False)
        self.wCircle.setVisible(False)
        self.wCube.setVisible(False)
        self.wSphere.setVisible(False)
        self.wPlane.setVisible(False)

        self.editorModel = editorModel
        self.editorModel.propSelected.connect(self.selectProp)
        self.editorModel.cutterPolyline.toolUpdated.connect(self.updateTool)
        self.editorModel.cutterRect.toolUpdated.connect(self.updateTool)
        self.editorModel.cutterCircle.toolUpdated.connect(self.updateTool)
        self.editorModel.cutterCube.toolUpdated.connect(self.updateTool)
        self.editorModel.cutterSphere.toolUpdated.connect(self.updateTool)
        self.editorModel.cutterPlane.toolUpdated.connect(self.updateTool)

        self.selectProp()
        self.updateTool()

    def setModel(self, model):
        self.editorModel = model
        self.editorModel.propSelected.connect(self.selectProp)
        self.editorModel.cutterPolyline.toolUpdated.connect(self.updateTool)
        self.editorModel.cutterRect.toolUpdated.connect(self.updateTool)
        self.editorModel.cutterCube.toolUpdated.connect(self.updateTool)
        self.editorModel.cutterCircle.toolUpdated.connect(self.updateTool)
        self.editorModel.cutterSphere.toolUpdated.connect(self.updateTool)
        self.editorModel.cutterPlane.toolUpdated.connect(self.updateTool)

        self.selectProp()
        self.updateTool()

    def selectProp(self):
        toggle = bool(self.editorModel.prop)
        self.pbPolyline.setEnabled(toggle)
        self.pbRect.setEnabled(toggle)
        self.pbCircle.setEnabled(toggle)
        self.pbCube.setEnabled(toggle)
        self.pbSphere.setEnabled(toggle)
        self.pbPlane.setEnabled(toggle)

    def updateTool(self):
        self.buttonGroup.setExclusive(False)
        self.pbPolyline.setChecked(self.editorModel.cutterPolyline.toggle)
        self.pbRect.setChecked(self.editorModel.cutterRect.toggle)
        self.pbCircle.setChecked(self.editorModel.cutterCircle.toggle)
        self.pbCube.setChecked(self.editorModel.cutterCube.toggle)
        self.pbSphere.setChecked(self.editorModel.cutterSphere.toggle)
        self.pbPlane.setChecked(self.editorModel.cutterPlane.toggle)
        self.buttonGroup.setExclusive(True)

        if self.editorModel.cutterPolyline.inverse:
            self.rbPolylineInverseYes.setChecked(True)
        else:
            self.rbPolylineInverseNo.setChecked(True)

        if self.editorModel.cutterRect.inverse:
            self.rbRectInverseYes.setChecked(True)
        else:
            self.rbRectInverseNo.setChecked(True)

        if self.editorModel.cutterCube.inverse:
            self.rbCubeInverseYes.setChecked(True)
        else:
            self.rbCubeInverseNo.setChecked(True)

        if self.editorModel.cutterSphere.inverse:
            self.rbSphereInverseYes.setChecked(True)
        else:
            self.rbSphereInverseNo.setChecked(True)

        self.wPolyline.setVisible(self.editorModel.cutterPolyline.toggle)
        self.wRect.setVisible(self.editorModel.cutterRect.toggle)
        self.wCircle.setVisible(self.editorModel.cutterCircle.toggle)
        self.wCube.setVisible(self.editorModel.cutterCube.toggle)
        self.wSphere.setVisible(self.editorModel.cutterSphere.toggle)
        self.wPlane.setVisible(self.editorModel.cutterPlane.toggle)

    @pyqtSlot(bool)
    def on_pbOpacity_toggled(self, toggle):
        if toggle:
            for prop in self.editorModel.props:
                # if prop != self.editorModel.prop:
                    self.editorModel.props[prop].opacity = 0.23
        else:
            for prop in self.editorModel.props:
                # if prop != self.editorModel.prop:
                    self.editorModel.props[prop].opacity = 1.0
        self.editorModel.propSelected.emit()
        log = open('C:/Users/Public/Documents/log_file.txt','a')
        log.write('Прозрачность'+'\n')
        log.close()


    @pyqtSlot(bool)
    def on_pbPolyline_toggled(self, toggle):
        self.editorModel.cutterPolyline.toggle = toggle

    @pyqtSlot(QAbstractButton)
    def on_bgPolylineInverse_buttonClicked(self, btn):
        inverse = self._getInverse(btn)
        self.editorModel.cutterPolyline.inverse = inverse

    @pyqtSlot()
    def on_pbPolylineCut_pressed(self):
        print('polyline cut')
        log = open('C:/Users/Public/Documents/log_file.txt','a')
        log.write('Обрезать контур'+'\n')
        log.close()

        self.editorModel.cutterPolyline.cut()

        if self.checkBoxClose.isChecked():
            prop = self.editorModel.prop
            if prop in self.editorModel.props:
                mesh = self.editorModel.props[prop].mesh
                mesh.close_mesh(inplace=True)

    @pyqtSlot(bool)
    def on_pbRect_toggled(self, toggle):
        self.editorModel.cutterRect.toggle = toggle

    @pyqtSlot(bool)
    def on_pbCircle_toggled(self, toggle):
        self.editorModel.cutterCircle.toggle = toggle

    @pyqtSlot(QAbstractButton)
    def on_bgRectInverse_buttonClicked(self, btn):
        inverse = self._getInverse(btn)
        self.editorModel.cutterRect.inverse = inverse

    @pyqtSlot()
    def on_pbRectCut_pressed(self):
        print('rect cut')
        log = open('C:/Users/Public/Documents/log_file.txt','a')
        log.write('Вырезать прямоугольник'+'\n')
        log.close()

        self.editorModel.cutterRect.cut()

        if self.checkBoxClose.isChecked():
            prop = self.editorModel.prop
            if prop in self.editorModel.props:
                mesh = self.editorModel.props[prop].mesh
                mesh.close_mesh(inplace=True)

    @pyqtSlot()
    def on_pbCircleCut_pressed(self):
        print('circle cut')
        log = open('C:/Users/Public/Documents/log_file.txt','a')
        log.write('Вырезать круг'+'\n')
        log.close()

        self.editorModel.cutterCircle.cut()

        if self.checkBoxClose.isChecked():
            prop = self.editorModel.prop
            if prop in self.editorModel.props:
                mesh = self.editorModel.props[prop].mesh
                mesh.close_mesh(inplace=True)

    @pyqtSlot(bool)
    def on_pbCube_toggled(self, toggle):
        self.editorModel.cutterCube.toggle = toggle

    @pyqtSlot(QAbstractButton)
    def on_bgCubeInverse_buttonClicked(self, btn):
        inverse = self._getInverse(btn)
        self.editorModel.cutterCube.inverse = inverse

    @pyqtSlot()
    def on_pbCubeCut_pressed(self):
        print('cube cut')
        log = open('C:/Users/Public/Documents/log_file.txt','a')
        log.write('Вырезать куб'+'\n')
        log.close()

        self.editorModel.cutterCube.cut()

        if self.checkBoxClose.isChecked():
            prop = self.editorModel.prop
            if prop in self.editorModel.props:
                mesh = self.editorModel.props[prop].mesh
                mesh.close_mesh(inplace=True)

    @pyqtSlot(bool)
    def on_pbSphere_toggled(self, toggle):
        self.editorModel.cutterSphere.toggle = toggle

    @pyqtSlot(QAbstractButton)
    def on_bgSphereInverse_buttonClicked(self, btn):
        inverse = self._getInverse(btn)
        self.editorModel.cutterSphere.inverse = inverse

    @pyqtSlot()
    def on_pbSphereCut_pressed(self):
        print('sphere cut')
        log = open('C:/Users/Public/Documents/log_file.txt','a')
        log.write('Вырезать шар'+'\n')
        log.close()

        self.editorModel.cutterSphere.cut()

        if self.checkBoxClose.isChecked():
            prop = self.editorModel.prop
            if prop in self.editorModel.props:
                mesh = self.editorModel.props[prop].mesh
                mesh.close_mesh(inplace=True)

    @pyqtSlot(bool)
    def on_pbPlane_toggled(self, toggle):
        self.editorModel.cutterPlane.toggle = toggle

    @pyqtSlot()
    def on_pbPlaneCut_pressed(self):
        print('plane cut')
        log = open('C:/Users/Public/Documents/log_file.txt','a')
        log.write('Вырезать плоскость'+'\n')
        log.close()

        self.editorModel.cutterPlane.close_mesh = self.checkBoxClose.isChecked()
        self.editorModel.cutterPlane.cut()

    def _getInverse(self, b):
        inverse = False
        if isinstance(b, QAbstractButton):
            if b.text() == 'Да':
                inverse = True
            else:
                inverse = False
        elif isinstance(b, QButtonGroup):
            if b.checkedButton().text() == 'Да':
                inverse = True
            else:
                inverse = False
        return inverse
