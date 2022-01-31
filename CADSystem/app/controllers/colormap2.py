from PyQt5.QtGui import QFontMetrics, QFont, QPainter, QColor
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QRectF, Qt
from PyQt5.QtWidgets import QWidget


class WindowLevelSlider(QWidget):
    CLICK_TYPE_WINDOW_MAX = 0
    CLICK_TYPE_WINDOW_BODY = 1
    CLICK_TYPE_WINDOW_MIN = 2

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self._click_pos = None
        self._click_type = None
        self._font = QFont('Decorative', 7)
        self._coordinates = {}
        self._window_x = 0
        self._window_h = 0

        fmw = QFontMetrics(self.font).width('-1024')
        self.setMinimumWidth(fmw + 20)
        self.setMaximumWidth(fmw + 20)

    def mousePressEvent(self, event):
        if (event.buttons() == Qt.LeftButton):
            self.click_pos = event.y()
            self.click_type = event.y()

    def mouseReleaseEvent(self, event):
        self.click_pos = None
        self.click_type = None

    def mouseMoveEvent(self, event):
        if WindowLevelSlider.CLICK_TYPE_WINDOW_MAX is self.click_type:
            self.moveWindowMax(self.click_pos - event.y())
        elif WindowLevelSlider.CLICK_TYPE_WINDOW_BODY is self.click_type:
            self.moveWindow(self.click_pos - event.y())
        elif WindowLevelSlider.CLICK_TYPE_WINDOW_MIN is self._click_type:
            self.moveWindowMin(self.click_pos - event.y())
        self.click_pos = event.y()

    @property
    def click_pos(self):
        return self._click_pos

    @click_pos.setter
    def click_pos(self, value):
        self._click_pos = value

    @property
    def click_type(self):
        return self._click_type

    @click_type.setter
    def click_type(self, value):
        if (value > self.window_x and (value < self.window_x + 5)):
            self._click_type = WindowLevelSlider.CLICK_TYPE_WINDOW_MAX
        elif (value > self.window_x + 5 and (value < self.window_x + self.window_h - 5)):
            self._click_type = WindowLevelSlider.CLICK_TYPE_WINDOW_BODY
        elif ((value > (self.window_x + self.window_h - 5)) and (value < self.window_x + self.window_h)):
            self._click_type = WindowLevelSlider.CLICK_TYPE_WINDOW_MIN
        else:
            self._click_type = None

    @property
    def window(self):
        return 400

    @property
    def level(self):
        return 50

    @property
    def font(self):
        return self._font

    @property
    def coordinates(self):
        self._coordinates = {}

        w = self.width()
        h = self.height()

        pix_size = h / sum(map(abs, [-1024, 1024]))

        text1 = 1024 - (1024 % 500)
        for p1 in range(int((1024 % 500) * pix_size), h, int(500 * pix_size)):
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
                density = 1024 - int(p3 / pix_size)
                if (density % 100) == 0:
                    density = round(1024 - (p3 / pix_size)) - 1
                self._coordinates[p3] = density

        return self._coordinates

    @property
    def window_x(self):
        self._window_x = self.getPixelByDensity(self.level + self.window / 2)

        return self._window_x

    @property
    def window_h(self):
        self._window_h = self.getPixelByDensity(
            self.level - self.window / 2) - self.window_x

        return self._window_h

    def getPixelByDensity(self, density):
        h = min(self.coordinates.values(), key=lambda x: abs(x - density))

        return list(self.coordinates.keys())[list(self.coordinates.values()).index(h)]

    def moveWindow(self, y):
        pix = self.getPixelByDensity(self.getLevel()) - y
        if (pix < 0):
            pix = 0
        if (pix > self.height() - 1):
            pix = self.height() - 1

        wc = self._coordinates[pix]
        self.setLevel(wc)

    def paintEvent(self, event):
        w = self.width()
        h = self.height()

        qp = QPainter(self)

        qp.setFont(self.font)
        self._fh = QFontMetrics(self.font).height()

        for p in self.coordinates:
            if ((self.coordinates[p] % 500) == 0):
                qp.drawLine(0, p, 15, p)

                txt = self._coordinates[p]
                qp.drawText(QRectF(20, p - (self._fh / 2), w, h),
                            Qt.AlignLeft, str(txt))
            elif ((self._coordinates[p] % 100) == 0):
                qp.drawLine(0, p, 5, p)

        qp.setPen(QColor(20, 20, 140))
        qp.setBrush(QColor(20, 20, 140, 70))
        qp.drawRect(0, self.window_x, 15, self.window_h)

        qp.setPen(QColor(20, 20, 140))
        qp.setBrush(QColor(20, 20, 140, 70))
        qp.drawRect(0, self.window_x, 15, 5)
        qp.drawRect(0, self.window_x + self.window_h - 5, 15, 5)


class ScalarBarWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent=parent)


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)

    slider = WindowLevelSlider()
    slider.showMaximized()

    sys.exit(app.exec_())
