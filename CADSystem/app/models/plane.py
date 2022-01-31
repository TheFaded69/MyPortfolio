from PyQt5.QtCore import QObject, pyqtSignal

from .image import imageModel


class PlaneModel(QObject):
    AXIAL = 2
    CORONAL = 1
    SAGITTAL = 0

    cmapUpdated = pyqtSignal()
    levelUpdated = pyqtSignal()
    windowUpdated = pyqtSignal()

    def __init__(self, parent=None, orientation=None):
        super().__init__(parent=parent)

        self._cmap = 'grayscale'
        self._level = 50
        self._window = 400

    @property
    def cmap(self):
        return self._cmap

    @cmap.setter
    def cmap(self, value):
        if self._cmap != value:
            self._cmap = value
            self.cmapUpdated.emit()

    @property
    def level(self):
        return self._level

    @level.setter
    def level(self, value):
        if self._level != value:
            self._level = value
            self.cmapUpdated.emit()

    @property
    def window(self):
        return self._window

    @window.setter
    def window(self, value):
        if self._window != value:
            self._window = value
            self.cmapUpdated.emit()


class PlaneModelOrientation(QObject):
    sliceUpdated = pyqtSignal()

    def __init__(self, parent, orientation):
        super().__init__(parent=parent)

        self.parent = parent
        self.cmapUpdated = self.parent.cmapUpdated

        self.orientation = orientation
        self.slice = 0

        self.imageModel = imageModel
        self.imageModel.imageLoaded.connect(self.loadImage)

    def loadImage(self):
        self.slice = int(self.slice_max / 2)

    @property
    def slice(self):
        return self._slice

    @slice.setter
    def slice(self, value):
        self._slice = value
        self.sliceUpdated.emit()

    @property
    def slice_max(self):
        slice_max = 0
        if self.orientation == PlaneModel.SAGITTAL:
            slice_max = self.imageModel.image.width
        elif self.orientation == PlaneModel.CORONAL:
            slice_max = self.imageModel.image.height
        elif self.orientation == PlaneModel.AXIAL:
            slice_max = self.imageModel.image.depth
        slice_max -= 1
        return slice_max

    @property
    def cmap(self):
        return self.parent.cmap

    @cmap.setter
    def cmap(self, value):
        self.parent.cmap = value

    @property
    def level(self):
        return self.parent.level

    @level.setter
    def level(self, value):
        self.parent.level = value

    @property
    def window(self):
        return self.parent.window

    @window.setter
    def window(self, value):
        self.parent.window = value


planeModel = PlaneModel()

axialModel = PlaneModelOrientation(parent=planeModel,
                                   orientation=PlaneModel.AXIAL)
coronalModel = PlaneModelOrientation(parent=planeModel,
                                     orientation=PlaneModel.CORONAL)
sagittalModel = PlaneModelOrientation(parent=planeModel,
                                      orientation=PlaneModel.SAGITTAL)
