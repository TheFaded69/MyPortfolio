from PyQt5.QtCore import QObject, pyqtSignal


class View3DModel(QObject):
    lookUpdated = pyqtSignal(int)
    modeUpdated = pyqtSignal()
    tissueUpdated = pyqtSignal()

    LOOK_AP = 0
    LOOK_PA = 1
    LOOK_LAO = 2
    LOOK_RAO = 3
    LOOK_SUP = 4
    LOOK_INF = 5
    LOOK_LL = 6
    LOOK_RL = 7

    MODE_VOLUME = 0
    MODE_MESH = 1
    MODE_CROSSHAIR = 2

    TISSUE_SKIN = 0
    TISSUE_BONE = 1
    TISSUE_MUSCLE = 2

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.mode = View3DModel.MODE_VOLUME
        self.tissue = View3DModel.TISSUE_BONE

    def setLook(self, look):
        self.lookUpdated.emit(look)

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, value):
        self._mode = value
        self.modeUpdated.emit()

    @property
    def tissue(self):
        return self._tissue

    @tissue.setter
    def tissue(self, value):
        self._tissue = value
        self.tissueUpdated.emit()


view3dModel = View3DModel()
