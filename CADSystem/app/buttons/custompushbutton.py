from PyQt5.QtWidgets import QPushButton


class CustomPushButton(QPushButton):

    def __init__(self, parent=None):
        super().__init__(parent=parent)

    def mouseReleaseEvent(self, event):
        if self.group().checkedId() == self.group().id(self):
            if self.isDown():
                self.group().setExclusive(False)
        super().mouseReleaseEvent(event)
        self.group().setExclusive(True)
