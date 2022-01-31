from PyQt5.QtCore import QObject, pyqtSignal


class LayoutModel(QObject):
    CLASSIC_BOTTOM = 0
    CLASSIC_RIGHT = 1
    ONLY_3D = 2
    TWO_BY_TWO = 3
    MIRRORING = 4
    ONLY_AXIAL = 5
    ONLY_CORONAL = 6
    ONLY_SAGITTAL = 7

    stateUpdated = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self._state = None

        self.state = LayoutModel.CLASSIC_RIGHT

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        if self._state != value:
            self._state = value
            self.stateUpdated.emit()


layoutModel = LayoutModel()
