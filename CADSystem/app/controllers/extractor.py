import vtk

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QWidget

from libcore.image import Image
from libcore.widget import ImageView
from libcore.qt import Viewport
from libcore.display import PolyActor

from ..models.look import LookModel, lookModel
from ..models.image import imageModel
from ..models.plane import planeModel
from ..models.editor import editorModel
from ..models.stage import stageModel

from ..views.extractor_ui import Ui_Extractor


class Extractor(QWidget, Ui_Extractor):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)

        self.viewport = Viewport()
        self.viewport.istyle = vtk.vtkInteractorStyleTrackballCamera()
        self.viewport.interactor.Initialize()
        self.layout.addWidget(self.viewport)

        self.view = None
        self.threshold.levelMinUpdated.connect(self.updateMinThreshold)
        self.threshold.levelMaxUpdated.connect(self.updateMaxThreshold)

        self.imageModel = imageModel
        self.imageModel.imageLoaded.connect(self.loadImage)

        self.lookModel = lookModel
        self.lookModel.lookUpdated.connect(self.updateLook)

        self.planeModel = planeModel
        self.planeModel.cmapUpdated.connect(self.updateCmap)
        self.planeModel.levelUpdated.connect(self.updateLevel)
        self.planeModel.windowUpdated.connect(self.updateWindow)

        self.editorModel = editorModel

        self.stageModel = stageModel

    def loadImage(self):
        if self.view:
            self.view.hide()
            self.view = None

        self.view = ImageView(self.viewport.interactor,
                              self.imageModel.image,
                              window=self.planeModel.window,
                              level=self.planeModel.level,
                              colormap=self.planeModel.cmap)
        self.view.on_windowlevel_changed = self.on_windowlevel
        self.view.on_cursor_changed = self.on_cursor
        self.view.contour_threshold = 400
        self.view.upper_threshold = 1500
        self.view.show()

        self.view.update_contours()
        self.updateRender()

        self.viewport.reset_view()
        self.viewport.look_from((0.4, -1.0, 0.4))
        self.viewport.zoom(1.35)

    def updateCmap(self):
        if self.view:
            self.view.colormap = self.planeModel.cmap

    def updateLevel(self):
        if self.view:
            self.view.level = self.planeModel.level

    def updateWindow(self):
        if self.view:
            self.view.window = self.planeModel.window

    def updateMinThreshold(self):
        if self.view:
            self.view.contour_threshold = self.threshold.ui.slider.level_min
            self.view.update_contours()
            self.updateRender()

    def updateMaxThreshold(self):
        if self.view:
            self.view.upper_threshold = self.threshold.ui.slider.level_max
            self.view.update_contours()
            self.updateRender()

    @pyqtSlot()
    def updateRender(self):
        self.viewport.rwindow.Render()

    def on_windowlevel(self, window, level):
        self.planeModel.level = level
        self.planeModel.window = window
        print('window: ', window)
        print('level: ', level)

    def on_cursor(self, cursor):
        print(cursor)
        self.updateRender()

    @pyqtSlot(tuple)
    def updateLook(self, look):
        self.viewport.look_from(look)

    def on_pbNext_pressed(self):
        log = open('C:/Users/Public/Documents/log_file.txt','a')
        log.write('Переход на следующий этап'+'\n')
        log.close()
        threshold = self.threshold.ui.slider.level_min
        threshold2 = self.threshold.ui.slider.level_max
        if threshold2 == 1500:
            discrete = False
        else:
            discrete = True

            
        mesh = self.imageModel.image.extract_surface(threshold=threshold,
                                                     threshold2=threshold2,
                                                     discrete=discrete)

        self.editorModel.addProp('mesh', PolyActor(mesh))
        self.stageModel.stage = 3
