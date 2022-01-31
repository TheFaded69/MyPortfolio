import datetime
import h5py

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QMainWindow, QFileDialog

from libcore.image import Image

from ..views.mainwindow_ui import Ui_MainWindow

from ..models.stage import stageModel
from ..models.editor import editorModel
from ..models.image import imageModel

from .previewdialog import PreviewDialog


class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)

        self.toggle = True

        # self.setWindow

        self.stageModel = stageModel
        self.stageModel.stageUpdated.connect(self.updateStage)

        # self.stages.setTabEnabled(1, False)
        # self.stages.setTabEnabled(1, True)
        self.on_stages_currentChanged(0)

        self.editorModel = editorModel
        self.editorModel.propsUpdated.connect(self.updateProps)

        self.imageModel = imageModel
        # self.imageModel.setImage(Image('libcore\\data\\rooster.vti'))

        self.stages.preprocessor.previewdialog.connect(self.showPreviewDialog)
        self.stages.editor.previewdialog.connect(self.showPreviewDialog)
        self.stages.implantor.previewdialog.connect(self.showPreviewDialog)

        self.statusBar().hide()

    def updateStage(self):
        stage = self.stages.tabText(self.stageModel.stage)
        # title = stage + " < CAD-система «Smart Implant» Версия: 0.45a"
        title = "Smart Implant"
        if self.windowTitle() != title:
            self.setWindowTitle(title)

    def updateProps(self):
        if len(self.editorModel.props) == 0:
            self.toggle = True
        elif len(self.editorModel.props) > 0 and self.toggle:
            self.toggle = False
            self.stages.editor.viewport.reset_view()

    @pyqtSlot(int)
    def on_stages_currentChanged(self, idx):
        self.stageModel.stage = idx

    @pyqtSlot()
    def on_actOpenProject_triggered(self):
        log = open('C:/Users/Public/Documents/log_file.txt','a')
        log.write('Открыть проект'+'\n')
        log.close()
        file_name, _ = QFileDialog.getOpenFileName(self,
                                                   "Открыть проект",
                                                   "",
                                                   "Файлы CADSI (*.cadsi)")
        if file_name:
            fd = h5py.File(file_name, 'r')
            self.imageModel.setImage(Image(Image.from_hdf(fd, 'image')))
            self.editorModel.load_from_hdf(fd)
            fd.close()

    @pyqtSlot()
    def on_actSaveProject_triggered(self):
        log = open('C:/Users/Public/Documents/log_file.txt','a')
        log.write('Сохранить проект'+'\n')
        log.close()
        file_name, _ = QFileDialog.getSaveFileName(self,
                                                   "Сохранить проект",
                                                   "",
                                                   "Файлы CADSI (*.cadsi)")
        if file_name:
            fd = h5py.File(file_name, 'w')
            if self.imageModel.image:
                self.imageModel.image.save_to_hdf(fd, 'image')
            if len(self.editorModel.props) > 0:
                self.editorModel.save_to_hdf(fd)
            fd.close()
            print(file_name)

    @pyqtSlot()
    def on_actExit_triggered(self):
        today = datetime.datetime.today()
        log = open('C:/Users/Public/Documents/log_file.txt','a')
        log.write('Конец работы: ' + today.strftime("%d-%m-%Y %H.%M.%S") + '\n')
        log.close()
        self.close()

    def showPreviewDialog(self):
        if not hasattr(self, 'pd'):
            self.pd = PreviewDialog(self)
        self.pd.showMaximized()

    @pyqtSlot()
    def on_actFullScreen_triggered(self):
         if self.isFullScreen() == 0:
            self.showFullScreen()
         else:
             self.showMaximized()
