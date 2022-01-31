from PyQt5.QtCore import QObject, pyqtSignal

from libcore.qt import Viewport


class LookModel(QObject):
    lookUpdated = pyqtSignal(tuple)

    AP = Viewport.OrientAnteriorPosterior
    PA = Viewport.OrientPosteriorAnterior
    LAO = Viewport.OrientLeftAnteriorOblique
    RAO = Viewport.OrientRightAnteriorOblique
    SUP = Viewport.OrientSuperiorInferior
    INF = Viewport.OrientInferiorSuperior
    LL = Viewport.OrientLeftLateral
    RL = Viewport.OrientRightLateral

    def __init__(self, parent=None):
        super().__init__(parent=parent)

    def setLook(self, look):
        self.lookUpdated.emit(look)


lookModel = LookModel()
