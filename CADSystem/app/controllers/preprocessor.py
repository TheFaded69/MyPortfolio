from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QWidget

from libcore import cmap

from ..views.preprocessor_ui import Ui_Preprocessor

from ..models.image import imageModel
from ..models.plane import PlaneModel, axialModel, coronalModel, sagittalModel
from ..models.stage import stageModel


class Preprocessor(QWidget, Ui_Preprocessor):
    previewdialog = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)

        self.colormap.setCmapHidden(True)
        self.view2d.tbTools.setHidden(True)

        self.imageModel = imageModel

        self.planeModel = axialModel
        self.planeModel.cmapUpdated.connect(self.updateCmap)

        self.stageModel = stageModel

        for color_name in cmap.cmaps():
            self.cbCmap.addItem(color_name)
        self.updateCmap()

    @pyqtSlot(str)
    def on_comboBoxOrientation_activated(self, orientation):
        self.view2d.setOrientation(orientation.lower())

    @pyqtSlot(str)
    def on_cbCmap_activated(self, cmap_name):
        self.planeModel.cmap = cmap_name

    @pyqtSlot()
    def on_pbOrigin_pressed(self):
        log = open('C:/Users/Public/Documents/log_file.txt', 'a')
        log.write('Отменить сглаживание'+'\n')
        log.close()
        self.imageModel.setOrigin()

    @pyqtSlot(float)
    def on_smoothSigma_valueChanged(self, sigma):
        self.smoothApply.setDisabled(False)

    @pyqtSlot(float)
    def on_smoothWindow_valueChanged(self, window):
        self.smoothApply.setDisabled(False)

    @pyqtSlot()
    def on_smoothApply_pressed(self):
        log = open('C:/Users/Public/Documents/log_file.txt', 'a')
        log.write('Сглаживание'+'\n')
        log.close()
        self.smoothApply.setDisabled(True)
        self.imageModel.setSmooth(self.smoothSigma.value(),
                                  self.smoothWindow.value())

    @pyqtSlot(int)
    def setDenoiseFactor(self, factor):
        self.denoiseApply.setDisabled(False)
        if self.denoiseFactor_2.value() != factor:
            self.denoiseFactor_2.setValue(factor)
        if self.denoiseFactor.value() != factor:
            self.denoiseFactor.setValue(factor)

    @pyqtSlot(int)
    def setDenoiseThreshold(self, threshold):
        self.denoiseApply.setDisabled(False)
        if self.denoiseThreshold_2.value() != threshold:
            self.denoiseThreshold_2.setValue(threshold)
        if self.denoiseThreshold.value() != threshold:
            self.denoiseThreshold.setValue(threshold)

    @pyqtSlot()
    def on_denoiseApply_pressed(self):
        log = open('C:/Users/Public/Documents/log_file.txt', 'a')
        log.write('Анизотропная фильтрация'+'\n')
        log.close()
        self.denoiseApply.setDisabled(True)
        self.imageModel.setDenoise(self.denoiseFactor.value(),
                                   self.denoiseThreshold.value())

    @pyqtSlot()
    def on_pushButtonEnhance_pressed(self):
        log = open('log_file.txt', 'a')
        log.write('Повышение резкости'+'\n')
        log.close()
        self.imageModel.setEnhance()

    @pyqtSlot()
    def on_pushButtonFlipX_pressed(self):
        log = open('C:/Users/Public/Documents/log_file.txt', 'a')
        log.write('Отзеркалить относительно Х'+'\n')
        log.close()
        self.imageModel.setFlip(axis='x')

    @pyqtSlot()
    def on_pushButtonFlipY_pressed(self):
        log = open('log_file.txt', 'a')
        log.write('Отзеркалить относительно Y'+'\n')
        log.close()
        self.imageModel.setFlip(axis='y')

    @pyqtSlot()
    def on_pushButtonFlipZ_pressed(self):
        log = open('C:/Users/Public/Documents/log_file.txt', 'a')
        log.write('Отзеркалить относительно Z'+'\n')
        log.close()
        self.imageModel.setFlip(axis='z')

    @pyqtSlot(bool)
    def on_toolButtonLineProbe_toggled(self, toggle):
        self.view2d.on_toolButtonLineProbe_toggled(toggle)

    @pyqtSlot()
    def on_toolButtonZoomIn_pressed(self):
        log = open('C:/Users/Public/Documents/log_file.txt', 'a')
        log.write('Увеличение масштаба'+'\n')
        log.close()
        self.view2d.viewport.camera.Zoom(1.1)
        self.view2d.viewport.rwindow.Render()

    @pyqtSlot()
    def on_toolButtonZoomOut_pressed(self):
        log = open('C:/Users/Public/Documents/log_file.txt', 'a')
        log.write('Уменьшение масштаба'+'\n')
        log.close()
        self.view2d.viewport.camera.Zoom(0.9)
        self.view2d.viewport.rwindow.Render()

    @pyqtSlot()
    def updateCmap(self):
        cmap_name = self.planeModel.cmap

        if self.cbCmap.currentText() != cmap_name:
            self.cbCmap.setCurrentText(cmap_name)
            print("{} set: {}".format(self.objectName(), cmap_name))

    def on_pushButtonPreview_pressed(self):
        log = open('C:/Users/Public/Documents/log_file.txt', 'a')
        log.write('Предпросмотр'+'\n')
        log.close()
        self.previewdialog.emit()

    def on_pbNext_pressed(self):
        log = open('C:/Users/Public/Documents/log_file.txt', 'a')
        log.write('Переход на следующий этап'+'\n')
        log.close()
        self.stageModel.stage = 2
