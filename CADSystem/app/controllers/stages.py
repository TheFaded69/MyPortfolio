from PyQt5.QtWidgets import QTabWidget

from ..views.stages_ui import Ui_Stages

from ..models.stage import stageModel
from ..models.image import imageModel
from ..models.editor import editorModel
from ..models.mirrorer import mirrorerModel
from ..models.implantor import implantorModel
from ..models.mounter import mounterModel
from ..models.printer import printerModel


class Stages(QTabWidget, Ui_Stages):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)

        for tab in range(1, 9):
            self.setTabEnabled(tab, False)

        self.stageModel = stageModel
        self.stageModel.stageUpdated.connect(self.updateStage)

        self.imageModel = imageModel
        self.imageModel.imageLoaded.connect(self.loadImage)

        self.editorModel = editorModel
        self.editorModel.propsUpdated.connect(self.updateProps)

        self.mirrorerModel = mirrorerModel
        self.mirrorerModel.meshLoaded.connect(self.loadMirrorer)

        self.implantorModel = implantorModel
        self.implantorModel.propsUpdated.connect(self.updateProps)

        self.mounterModel = mounterModel
        self.mounterModel.loaded.connect(self.loadMounter)

        self.printerModel = printerModel
        self.printerModel.loaded.connect(self.loadPrinter)

    def updateStage(self):
        if self.stageModel.stage != self.currentIndex():
            self.setCurrentIndex(self.stageModel.stage)

    def loadImage(self):
        self.setTabEnabled(1, True)
        self.setTabEnabled(2, True)

    def updateProps(self):
        if len(self.editorModel.props) > 0:
            if not self.isTabEnabled(3):
                self.setTabEnabled(3, True)
        if len(self.implantorModel.props) > 0:
            if not self.isTabEnabled(5):
                self.implantor.viewport.reset_view()
                self.setTabEnabled(5, True)

    def loadMirrorer(self):
        log = open('C:/Users/Public/Documents/log_file.txt', 'a')
        log.write('Загрузка этапа поиска недостающего объема'+'\n')
        log.close()
        self.setTabEnabled(4, True)

    def loadMounter(self):
        log = open('C:/Users/Public/Documents/log_file.txt', 'a')
        log.write('Загрузка этапа конструктора креплений'+'\n')
        log.close()
        self.setTabEnabled(6, True)

    def loadPrinter(self):
        log = open('C:/Users/Public/Documents/log_file.txt', 'a')
        log.write('Загрузка этапа печати'+'\n')
        log.close()
        self.setTabEnabled(7, True)
