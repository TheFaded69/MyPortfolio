from PyQt5.QtCore import QObject, pyqtSignal


class StageModel(QObject):
    stageUpdated = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)

    @property
    def stage(self):
        return self._stage

    @stage.setter
    def stage(self, value):
        self._stage = value
        self.stageUpdated.emit()


stageModel = StageModel()
