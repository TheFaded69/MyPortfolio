from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

from libcore.image import Image


class ImageModel(QObject):
    imageLoaded = pyqtSignal()
    imageUpdated = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.origin = None
        self.image = None
        self.files = None
        self._uid = None

    @property
    def uid(self):
        return self._uid

    @uid.setter
    def uid(self, val):
        import random
        rng = random.Random()
        rng.seed(val.strip().lower())
        syms = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F']
        self._uid = ''.join(rng.choices(syms, k=8))

    @pyqtSlot(Image)
    def setImage(self, image):
        self.origin = Image(image)
        self.image = image
        self.imageLoaded.emit()

    @pyqtSlot(float, float)
    def setSmooth(self, sigma, window):
        if self.image:
            self.image.smooth(sigma=sigma,
                              window=window,
                              inplace=True)
            self.imageUpdated.emit()

    @pyqtSlot(float, float)
    def setDenoise(self, factor, threshold):
        if self.image:
            self.image.denoise(factor=factor,
                               threshold=threshold,
                               inplace=True)
            self.imageUpdated.emit()

    @pyqtSlot()
    def setEnhance(self):
        if self.image:
            self.image.enhance(inplace=True)
            self.imageUpdated.emit()

    @pyqtSlot()
    def setOrigin(self):
        if self.image:
            self.image = Image(self.origin)
            self.imageLoaded.emit()

    @pyqtSlot(str)
    def setFlip(self, axis='x'):
        if self.image:
            self.image.flip(axis=axis, inplace=True)
            self.imageUpdated.emit()


imageModel = ImageModel()
