from PyQt5.QtGui import QFontMetrics, QFont, QPainter, QColor
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QRectF, Qt
from PyQt5.QtWidgets import QWidget

from libcore import color

from ..models.image import imageModel
from ..models.plane import planeModel


class Colormap(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        from ..views.colormap_ui import Ui_Colormap
        self.ui = Ui_Colormap()
        self.ui.setupUi(self)

        self.setDisabled(True)

        self.setMaximumWidth(86)

        self.imageModel = imageModel
        self.imageModel.imageLoaded.connect(self.loadImage)

        self.planeModel = planeModel
        self.planeModel.cmapUpdated.connect(self.updateCmap)
        self.planeModel.cmapUpdated.connect(self.updateLevel)
        self.planeModel.cmapUpdated.connect(self.updateWindow)

    @pyqtSlot(bool)
    def setCmapHidden(self, toggle):
        self.ui.comboBoxCmap.setHidden(toggle)

    @pyqtSlot(str)
    def setCmap(self, cmap_name):
        if self.planeModel:
            self.planeModel.cmap = cmap_name

    @pyqtSlot(int)
    def setLevel(self, level):
        if self.planeModel:
            self.planeModel.level = level

    @pyqtSlot(int)
    def setWindow(self, window):
        if self.planeModel:
            self.planeModel.window = window

    @pyqtSlot()
    def loadImage(self):
        self.setEnabled(True)

        for color_name in color.cmaps():
            self.ui.comboBoxCmap.addItem(color_name)

        if self.imageModel.image:
            if self.imageModel.image.modality == 'mri':
                self.planeModel.level = 800
                self.planeModel.window = 2000
            else:
                self.planeModel.level = 50
                self.planeModel.window = 400

        self.updateCmap()
        self.updateLevel()
        self.updateWindow()

        self.ui.spinBoxLevel.setRange(-2048, 2048)
        self.ui.spinBoxWindow.setRange(255, 4096)

        print("{} image loaded".format(self.objectName()))

    @pyqtSlot()
    def updateCmap(self):
        cmap_name = self.planeModel.cmap

        if self.ui.comboBoxCmap.currentText() != cmap_name:
            self.ui.comboBoxCmap.setCurrentText(cmap_name)

        self.ui.bar.setCmap(color.cmap(cmap_name))
        print("{} set: {}".format(self.objectName(), cmap_name))

    @pyqtSlot()
    def updateLevel(self):
        level = self.planeModel.level

        if self.ui.slider.getLevel() != level:
            self.ui.slider.setLevel(level)
        if self.ui.spinBoxLevel.value() != level:
            self.ui.spinBoxLevel.setValue(level)

    @pyqtSlot()
    def updateWindow(self):
        window = self.planeModel.window

        if self.ui.slider.getWindow() != window:
            self.ui.slider.setWindow(window)
        if self.ui.spinBoxWindow.value() != window:
            self.ui.spinBoxWindow.setValue(window)


class DensityWindowSlider(QWidget):
    windowChanged = pyqtSignal(int)
    levelChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self._levelChanged = 50
        self._window = 400

        self._densities = [-2048, 2048]

        self._click_type = None
        self._click_pos = None

        self._coordinates = {}

        self._font = QFont('Decorative', 7)
        fmw = QFontMetrics(self._font).width(str(self.getDensityMin()))
        self.setMinimumWidth(fmw + 20)
        self.setMaximumWidth(fmw + 20)

    def mousePressEvent(self, event):
        if (event.buttons() == Qt.LeftButton):
            self._click_pos = event.y()
            self._click_type = self.getPixType(event.y())

    def mouseReleaseEvent(self, event):
        self._click_pos = None
        self._click_type = None

    def mouseMoveEvent(self, event):
        if (self._click_type == 1):
            self.moveWindowMax(self._click_pos - event.y())
        elif (self._click_type == 2):
            self.moveWindow(self._click_pos - event.y())
        elif (self._click_type == 3):
            self.moveWindowMin(self._click_pos - event.y())
        self._click_pos = event.y()

    def moveWindow(self, y):
        pix = self.getPixelByDensity(self.getLevel()) - y
        if (pix < 0):
            pix = 0
        if (pix > self.height() - 1):
            pix = self.height() - 1

        wc = self._coordinates[pix]
        self.setLevel(wc)

    def moveWindowMin(self, y):
        pix_size = self.height() / sum(map(abs, self.getDensities()))
        ww = int(self.getWindow() - (y / pix_size) * 2)
        self.setWindow(ww)

    def moveWindowMax(self, y):
        pix_size = self.height() / sum(map(abs, self.getDensities()))
        ww = int(self.getWindow() + (y / pix_size) * 2)
        self.setWindow(ww)

    def paintEvent(self, event):
        w = self.width()
        h = self.height()

        qp = QPainter(self)

        qp.setFont(self._font)
        self._fh = QFontMetrics(self._font).height()

        self.updateCoordinates()

        for p in self._coordinates:
            if ((self._coordinates[p] % 500) == 0):
                qp.drawLine(0, p, 15, p)

                txt = self._coordinates[p]
                if txt == 2000:
                    txt = 1000
                elif txt == 1500:
                    txt = 750
                elif txt == 1000:
                    txt = 500
                elif txt == 500:
                    txt = 250
                elif txt == -500:
                    txt = -250
                elif txt == -1000:
                    txt = -500
                elif txt == -1500:
                    txt = -750
                elif txt == -2000:
                    txt = -1000

                qp.drawText(QRectF(20, p - (self._fh / 2), w, h),
                            Qt.AlignLeft, str(txt))
            elif ((self._coordinates[p] % 100) == 0):
                qp.drawLine(0, p, 5, p)

        self.updateWindowVars()

        qp.setPen(QColor(20, 20, 140))
        qp.setBrush(QColor(20, 20, 140, 70))
        qp.drawRect(0, self.window_x, 15, self.window_h)

        qp.setPen(QColor(20, 20, 140))
        qp.setBrush(QColor(20, 20, 140, 70))
        qp.drawRect(0, self.window_x, 15, 5)
        qp.drawRect(0, self.window_x + self.window_h - 5, 15, 5)

    def getPixelByDensity(self, density):
        h = min(self._coordinates.values(), key=lambda x: abs(x - density))
        return list(self._coordinates.keys())[list(self._coordinates.values()).index(h)]

    def getPixType(self, y):
        if (y > self.window_x and (y < self.window_x + 5)):
            return 1
        elif (y > self.window_x + 5 and (y < self.window_x + self.window_h - 5)):
            return 2
        elif ((y > (self.window_x + self.window_h - 5)) and (y < self.window_x + self.window_h)):
            return 3
        else:
            return 0

    def updateWindowVars(self):
        self.window_x = self.getPixelByDensity(
            self._levelChanged + self._window / 2)
        self.window_h = self.getPixelByDensity(
            self._levelChanged - self._window / 2) - self.window_x

    def updateCoordinates(self):
        self._coordinates = {}

        w = self.width()
        h = self.height()

        pix_size = h / sum(map(abs, self.getDensities()))

        text1 = self.getDensityMax() - (self.getDensityMax() % 500)
        # координаты значений
        for p1 in range(int((self.getDensityMax() % 500) * pix_size), h, int(500 * pix_size)):
            self._coordinates[p1] = text1

            text2 = text1
            for g in range(100, 500, 100):
                text2 -= 100
                p2 = int(p1 + (g * pix_size))
                if p2 > h:
                    break
                self._coordinates[p2] = text2

            text1 -= 500

        for p3 in range(0, h):
            if p3 not in self._coordinates:
                density = self.getDensityMax() - int(p3 / pix_size)
                if (density % 100) == 0:
                    density = round(self.getDensityMax() - (p3 / pix_size)) - 1
                self._coordinates[p3] = density

    @pyqtSlot(int)
    def setLevel(self, val):
        center_min = self.getDensityMin() + self.getWindow() / 2
        center_max = self.getDensityMax() - self.getWindow() / 2

        if (val < center_min):
            val = center_min
        if (val > center_max):
            val = center_max

        self._levelChanged = val
        self.levelChanged.emit(val)
        self.update()

    @pyqtSlot(int)
    def setWindow(self, val):
        if (val < 255):
            val = 255

        self._window = val
        self.windowChanged.emit(val)
        self.update()

    def getLevel(self):
        return self._levelChanged

    def getWindow(self):
        return self._window

    def getDensities(self):
        return self._densities

    def getDensityMin(self):
        return self._densities[0]

    def getDensityMax(self):
        return self._densities[1]

    def setDensities(self, densities=[]):
        self._densities = densities
        self.update()


class ScalarBarWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self._lookup_table = None
        self._densities = [0, 0]

    def setCmap(self, lut):
        self._lookup_table = lut
        self._densities = list(map(int, self._lookup_table.GetTableRange()))

        self._font = QFont('Decorative', 8)
        self._fm = QFontMetrics(self._font)
        self._fmw = self._fm.width(str(self._densities[0]))
        self._fmh = self._fm.height()
        self.setMinimumWidth(self._fmw + 15)
        self.setMaximumWidth(self._fmw + 15)

        self.update()

    def drawText(self, qp):
        d = (self._densities[1] - self._densities[0])

        txt = str(self._densities[1])
        txt_w = self._fm.width(txt)
        x = 0
        y = 0
        w = self.width()
        h = self._fmh
        qp.setPen(QColor(255, 255, 255))
        qp.setBrush(QColor(255, 255, 255))
        qp.drawRect(w - txt_w - 2, y, w, h)
        qp.setPen(QColor(0, 0, 0))
        qp.drawText(x, y, w, h, Qt.AlignRight, str(1000))

        txt = str(int(self._densities[1] - d * 0.25))
        txt_w = self._fm.width(txt)
        x = 0
        y = self.height() * 0.25 - self._fmh / 2
        w = self.width()
        h = self._fmh
        qp.setPen(QColor(255, 255, 255))
        qp.setBrush(QColor(255, 255, 255))
        qp.drawRect(w - txt_w - 2, y, w, h)
        qp.setPen(QColor(0, 0, 0))
        qp.drawText(x, y, w, h, Qt.AlignRight, str(500))

        txt = str(int(self._densities[1] - d * 0.5))
        txt_w = self._fm.width(txt)
        x = 0
        y = self.height() * 0.5 - self._fmh / 2
        w = self.width()
        h = self._fmh
        qp.setPen(QColor(255, 255, 255))
        qp.setBrush(QColor(255, 255, 255))
        qp.drawRect(w - txt_w - 2, y, w, h)
        qp.setPen(QColor(0, 0, 0))
        qp.drawText(x, y, w, h, Qt.AlignRight, txt)

        txt = str(int(self._densities[1] - d * 0.75))
        txt_w = self._fm.width(txt)
        x = 0
        y = self.height() * 0.75 - self._fmh / 2
        w = self.width()
        h = self._fmh
        qp.setPen(QColor(255, 255, 255))
        qp.setBrush(QColor(255, 255, 255))
        qp.drawRect(w - txt_w - 2, y, w, h)
        qp.setPen(QColor(0, 0, 0))
        qp.drawText(x, y, w, h, Qt.AlignRight, str(-500))

        txt = str(self._densities[0])
        txt_w = self._fm.width(txt)
        x = 0
        y = self.height() - self._fmh
        w = self.width()
        h = self._fmh
        qp.setPen(QColor(255, 255, 255))
        qp.setBrush(QColor(255, 255, 255))
        qp.drawRect(w - txt_w - 2, y, w, h)
        qp.setPen(QColor(0, 0, 0))
        qp.drawText(x, y, w, h, Qt.AlignRight, str(-1000))

    def paintEvent(self, event):
        if self._lookup_table is None:
            return

        qp = QPainter(self)

        w = self.width()
        h = self.height()

        g = self._lookup_table.GetNumberOfAvailableColors() / h

        for y in range(h):
            color = self._lookup_table.GetTable().GetTuple4(int(y * g))
            qp.setPen(QColor(color[0], color[1], color[2], color[3]))
            qp.drawLine(0, h - y, w, h - y)

        self.drawText(qp)
