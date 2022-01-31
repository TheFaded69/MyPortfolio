from PyQt5.QtCore import pyqtSlot, pyqtSignal, Qt
from PyQt5.QtWidgets import QWidget

from ..views.meshtools_ui import Ui_MeshTools

from ..models.editor import EditorModel, editorModel


class MeshTools(QWidget, Ui_MeshTools):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)

        self.wSplit.setHidden(True)
        self.wSmooth.setHidden(True)
        self.lRuler3D.setHidden(True)

        self.editorModel = editorModel
        self.editorModel.propSelected.connect(self.selectProp)
        self.editorModel.splitter.toolUpdated.connect(self.updateTool)

        self.selectProp()

    def setModel(self, model):
        self.editorModel = model
        self.editorModel.propSelected.connect(self.selectProp)
        self.editorModel.splitter.toolUpdated.connect(self.updateTool)

        self.selectProp()

    def selectProp(self):
        toggle = bool(self.editorModel.prop)

        self.pushButtonFlipX.setEnabled(toggle)
        self.pbClose.setEnabled(toggle)
        self.pbFill.setEnabled(toggle)
        self.pbSplit.setEnabled(toggle)
        self.pbSmooth.setEnabled(toggle)

    def on_pushButtonFlipX_pressed(self):
        log = open('log_file.txt','a')
        log.write('Зеркальное отображение относительно Х'+'\n')
        log.close()
        if self.editorModel.prop:
            self.editorModel.props[self.editorModel.prop].mesh.reflect(plane='x', inplace=True)
        self.editorModel.propsUpdated.emit()

    def on_pushButtonFlipY_pressed(self):
        log = open('log_file.txt','a')
        log.write('Зеркальное отображение относительно Y'+'\n')
        log.close()
        if self.editorModel.prop:
            self.editorModel.props[self.editorModel.prop].mesh.reflect(plane='y', inplace=True)
        self.editorModel.propsUpdated.emit()

    def on_pushButtonFlipZ_pressed(self):
        log = open('log_file.txt','a')
        log.write('Зеркальное отображение относительно Z'+'\n')
        log.close()
        if self.editorModel.prop:
            self.editorModel.props[self.editorModel.prop].mesh.reflect(plane='z', inplace=True)
        self.editorModel.propsUpdated.emit()

    def updateTool(self, tool):
        if tool.name == 'splitter':
            self.pbSplit.setChecked(tool.toggle)

            self.wSplit.setVisible(tool.toggle)

            number = self.editorModel.splitter.number
            if number != self.sbSplitNumber.value():
                self.sbSplitNumber.setValue(number)

            size = self.editorModel.splitter.size
            if size != self.cbSplitSize.currentIndex():
                self.hsSplitSize.setCurrentIndex(size)

    def on_pbClose_pressed(self):
        log = open('log_file.txt','a')
        log.write('Закрыть контура'+'\n')
        log.close()
        print("close")
        if self.editorModel.prop:
            prop = self.editorModel.props[self.editorModel.prop]
            prop.mesh.close_mesh(inplace=True)

    def on_pbFill_pressed(self):
        log = open('log_file.txt','a')
        log.write('Заполнить дыры'+'\n')
        log.close()
        print("fill")
        if self.editorModel.prop:
            prop = self.editorModel.props[self.editorModel.prop]
            prop.mesh.fill_holes(inplace=True)

    def on_pbSmooth_toggled(self, toggle):
        self.wSmooth.setVisible(toggle)

    def on_pbSmoothApply_pressed(self):
        log = open('log_file.txt','a')
        log.write('Применить сглаживание'+'\n')
        log.close()
        iterations = self.sbIterations.value()
        if self.editorModel.prop in self.editorModel.props:
            prop = self.editorModel.props[self.editorModel.prop]
            print('I am about to smooth shit of the mesh')
            prop.mesh.smooth(iterations=iterations, inplace=True)

        # if self.editorModel.prop in self.editorModel.props:
        #    prop = self.editorModel.props[self.editorModel.prop]
        #    prop.mesh.subdivide(algorithm='butterfly', inplace=True)

    @pyqtSlot(bool)
    def on_pbSplit_toggled(self, toggle):
        self.editorModel.splitter.toggle = toggle

    @pyqtSlot(int)
    def on_sbSplitNumber_valueChanged(self, value):
        self.editorModel.splitter.number = value

    @pyqtSlot(int)
    def on_cbSplitSize_activated(self, value):
        self.editorModel.splitter.size = value

    def on_pbSplitApply_pressed(self):
        log = open('C:/Users/Public/Documents/log_file.txt', 'a')
        log.write('Разделить по размеру' + '\n')
        log.close()
        self.editorModel.splitter.cut()

    def on_pbSplitSplit_pressed(self):
        log = open('C:/Users/Public/Documents/log_file.txt','a')
        log.write('Разделить'+'\n')
        log.close()
        self.editorModel.splitter.split()

    def on_pbCrossSection_toggled(self, toggle):
        if toggle:
            self.on_pbRuler3D_toggled(False)
        self.pbCrossSection.setChecked(toggle)
        self.editorModel.crossSectionUpdated.emit(toggle)

    def on_pbRuler3D_toggled(self, toggle):
        log = open('C:/Users/Public/Documents/log_file.txt','a')
        log.write('Запуск 3D измерителя'+'\n')
        log.close()
        if toggle:
            self.on_pbCrossSection_toggled(False)
            self.lRuler3D.setVisible(True)
        else:
            self.lRuler3D.setVisible(False)
        self.pbRuler3D.setChecked(toggle)
        self.editorModel.ruler3DUpdated.emit(toggle)
