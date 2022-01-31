from PyQt5.QtCore import QObject, pyqtSignal


class HistogramModel(QObject):
    histogramUpdated = pyqtSignal()
    histogramEnabled = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.histogram = None

    def showHistogram(self, toggle):
        self.histogramEnabled.emit(toggle)

    def setHistogram(self, samples):
        self.histogram = samples
        self.histogramUpdated.emit()


histogramModel = HistogramModel()
