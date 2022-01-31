from PyQt5.QtCore import QObject, pyqtSignal


class MirrorerModel(QObject):
    meshLoaded = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self._mesh = None

    @property
    def mesh(self):
        return self._mesh

    @mesh.setter
    def mesh(self, value):
        self._mesh = value
        self.meshLoaded.emit()


mirrorerModel = MirrorerModel()
