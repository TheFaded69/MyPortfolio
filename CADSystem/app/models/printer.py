from PyQt5.QtCore import QObject, pyqtSignal


class PrinterModel(QObject):
    loaded = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self._implant = None
        self._cylinders = None

    @property
    def implant(self):
        return self._implant

    @implant.setter
    def implant(self, value):
        self._implant = value
        self.loaded.emit()

    @property
    def cylinders(self):
        return self._cylinders

    @cylinders.setter
    def cylinders(self, value):
        self._cylinders = value


printerModel = PrinterModel()
