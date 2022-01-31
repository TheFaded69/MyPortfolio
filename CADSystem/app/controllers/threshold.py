from PyQt5.QtGui import QFont, QFontMetrics, QPainter, QColor
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QRectF, Qt
from PyQt5.QtWidgets import QWidget


class Threshold(QWidget):
    levelMinUpdated = pyqtSignal(int)
    levelMaxUpdated = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        from ..views.threshold_ui import Ui_Threshold
        self.ui = Ui_Threshold()
        self.ui.setupUi(self)

        self.ui.sbLevelMax.setSingleStep(-1)
        self.ui.sbLevelMax.setRange(self.ui.slider.density_min,
                                    self.ui.slider.density_max)
        self.ui.sbLevelMin.setSingleStep(-1)
        self.ui.sbLevelMin.setRange(self.ui.slider.density_min,
                                    self.ui.slider.density_max)

        self.ui.slider.levelMinUpdated.connect(self.updateLevelMin)
        self.ui.slider.levelMaxUpdated.connect(self.updateLevelMax)

        self.updateLevelMin()
        self.updateLevelMax()

        self.setMinimumWidth(35)
        self.setMaximumWidth(35)

    def updateLevelMin(self):
        level = self.ui.slider.level_min
        if self.ui.sbLevelMin.value() != level:
            self.ui.sbLevelMin.setValue(level)

            self.levelMinUpdated.emit(level)

    def updateLevelMax(self):
        level = self.ui.slider.level_max
        if self.ui.sbLevelMax.value() != level:
            self.ui.sbLevelMax.setValue(level)

            self.levelMaxUpdated.emit(level)

    @pyqtSlot(int)
    def on_sbLevelMax_valueChanged(self, value):
        self.ui.slider.level_max = value

    @pyqtSlot(int)
    def on_sbLevelMin_valueChanged(self, value):
        self.ui.slider.level_min = value


class ThresholdSlider(QWidget):
    levelMinUpdated = pyqtSignal()
    levelMaxUpdated = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self._level_min = None
        self._level_max = None
        self._densities = [-2048, 2048]

        self._click_type = None
        self._click_pos = None

        self._coordinates = {}

        self.level_min = 400
        self.level_max = 1500
        self.densities = [-2048, 2048]

        # maximum width
        self._font = QFont('Decorative', 7)
        fmw = QFontMetrics(self._font).width(str(self.density_min))
        self.setMinimumWidth(35)
        self.setMaximumWidth(35)
        # self.setMinimumWidth(fmw + 20)
        # self.setMaximumWidth(fmw + 20)

    @property
    def level_min(self):
        return self._level_min

    @level_min.setter
    def level_min(self, value):
        if self.level_min != value:
            self._level_min = value
            self.update()
            self.levelMinUpdated.emit()

    @property
    def level_max(self):
        return self._level_max

    @level_max.setter
    def level_max(self, value):
        if self.level_max != value:
            self._level_max = value
            self.update()
            self.levelMaxUpdated.emit()

    @property
    def densities(self):
        return self._densities

    @property
    def density_min(self):
        return self.densities[0]

    @property
    def density_max(self):
        return self.densities[1]

    @densities.setter
    def densities(self, value):
        self._densities = value
        self.update()

    def mousePressEvent(self, event):
        if (event.buttons() == Qt.LeftButton):
            self._click_type = self.getTypeByPixel(event.y())
            self._click_pos = event.y()

    def mouseMoveEvent(self, event):
        if self._click_type == 1:
            self.moveLevelMax(self._click_pos - event.y())
        elif self._click_type == 2:
            self.moveLevel(self._click_pos - event.y())
        elif self._click_type == 3:
            self.moveLevelMin(self._click_pos - event.y())
        self._click_pos = event.y()

    def mouseReleaseEvent(self, event):
        self._click_type = None
        self._click_pos = None

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
                # qp.drawText(QRectF(20, p - (self._fh / 2), w, h),
                #             Qt.AlignLeft,
                #             str(self._coordinates[p]))
            elif ((self._coordinates[p] % 100) == 0):
                qp.drawLine(0, p, 5, p)

        self.updateLevelVars()

        qp.setPen(QColor(20, 20, 140))
        qp.setBrush(QColor(20, 140, 20, 70))
        qp.drawRect(0, self.window_x, 15, self.window_h)

        qp.setPen(QColor(20, 140, 140))
        qp.setBrush(QColor(20, 140, 20, 100))
        qp.drawRect(0, self.window_x, 15, 5)
        qp.drawRect(0, self.window_x + self.window_h - 5, 15, 5)

    def moveLevel(self, y):
        self.moveLevelMin(y)
        self.moveLevelMax(y)

    def moveLevelMin(self, y):
        pix = self.getPixelByDensity(self.level_min) - y
        if pix < 0:
            pix = 0
        elif pix > self.height() - 1:
            pix = self.height() - 1
        elif pix < self.getPixelByDensity(self.level_max - 50):
            pix = self.getPixelByDensity(self.level_max - 50)

        wc = self._coordinates[pix]
        self.level_min = wc

    def moveLevelMax(self, y):
        pix = self.getPixelByDensity(self.level_max) - y
        if pix < 0:
            pix = 0
        elif pix > self.height() - 1:
            pix = self.height() - 1
        elif pix > self.getPixelByDensity(self.level_min + 50):
            pix = self.getPixelByDensity(self.level_min + 50)

        wc = self._coordinates[pix]
        self.level_max = wc

    def getPixelByDensity(self, density):
        h = min(self._coordinates.values(), key=lambda x: abs(x - density))
        return list(self._coordinates.keys())[list(self._coordinates.values()).index(h)]

    def getTypeByPixel(self, y):
        if (y > self.window_x and (y < self.window_x + 5)):
            return 1
        elif (y > self.window_x + 5 and (y < self.window_x + self.window_h - 5)):
            return 2
        elif ((y > (self.window_x + self.window_h - 5)) and (y < self.window_x + self.window_h)):
            return 3
        else:
            return 0

    def updateCoordinates(self):
        self._coordinates = {}

        w = self.width()
        h = self.height()

        pix_size = h / sum(map(abs, self.densities))

        text1 = self.density_max - (self.density_max % 500)
        # координаты значений
        for p1 in range(int((self.density_max % 500) * pix_size), h, int(500 * pix_size)):
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
                density = self.density_max - int(p3 / pix_size)
                if (density % 100) == 0:
                    density = round(self.density_max - (p3 / pix_size)) - 1
                self._coordinates[p3] = density

    def updateLevelVars(self):
        self.window_x = self.getPixelByDensity(self.level_max)
        self.window_h = self.getPixelByDensity(self.level_min) - self.window_x
