import vtk

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QWidget

from libcore.qt import Viewport
from libcore.display import VolActor

from ..models.image import imageModel
from ..models.look import lookModel

from ..views.view3d_ui import Ui_View3D


class View3D(QWidget, Ui_View3D):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)

        self.viewport = Viewport()
        self.viewport.istyle = vtk.vtkInteractorStyleTrackballCamera()
        self.viewport.interactor.Initialize()
        self.layout.addWidget(self.viewport)

        self.imageModel = imageModel
        self.imageModel.imageLoaded.connect(self.loadImage)
        self.imageModel.imageUpdated.connect(self.updateImage)

        self.lookModel = lookModel
        self.lookModel.lookUpdated.connect(self.updateLook)

        self.loadImage()

    @pyqtSlot()
    def loadImage(self):
        if self.imageModel.image:
            if hasattr(self, 'actor'):
                self.viewport.remove_prop(self.actor)
            self.actor = VolActor(self.imageModel.image)
            self.viewport.add_prop(self.actor)
            self.viewport.reset_view()

    @pyqtSlot()
    def updateImage(self):
        if self.imageModel.image:
            self.viewport.remove_prop(self.actor)
            self.actor = VolActor(self.imageModel.image)
            self.viewport.add_prop(self.actor)
            self.updateRender()

    @pyqtSlot(tuple)
    def updateLook(self, look):
        self.viewport.look_from(look)

    def updateRender(self):
        self.viewport.rwindow.Render()
