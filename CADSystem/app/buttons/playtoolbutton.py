from PyQt5.QtWidgets import QToolButton, QMenu, QAction, QActionGroup
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtGui import QIcon


class PlayToolButton(QToolButton):

    def __init__(self, parent=None, toolBar=None, action=None, callback=None):
        super().__init__(parent)

        self._state = True
        self._loop = False
        self._frames_per_second = 5

        if toolBar is not None:
            if action is not None:
                toolBar.insertWidget(action, self)
                toolBar.removeAction(action)

        if callback is not None:
            self.pressed.connect(callback)
        self.pressed.connect(self.stateChanged)

        self.setText('Play')
        self.setIcon(QIcon(':/icons/play.png'))
        self.setPopupMode(QToolButton.MenuButtonPopup)

        frame_5_act = QAction('5 frame per second', self,
                              checkable=True, checked=True)
        frame_5_act.setData(5)
        frame_10_act = QAction('10 frame per second', self, checkable=True)
        frame_10_act.setData(10)
        frame_15_act = QAction('15 frame per second', self, checkable=True)
        frame_15_act.setData(15)
        frame_20_act = QAction('20 frame per second', self, checkable=True)
        frame_20_act.setData(20)
        frame_25_act = QAction('25 frame per second', self, checkable=True)
        frame_25_act.setData(25)

        ag = QActionGroup(self, exclusive=True)
        ag.triggered.connect(self.framesPerSecondChanded)
        ag.addAction(frame_5_act)
        ag.addAction(frame_10_act)
        ag.addAction(frame_15_act)
        ag.addAction(frame_20_act)
        ag.addAction(frame_25_act)

        self.menu = QMenu(self)
        self.menu.addAction(frame_5_act)
        self.menu.addAction(frame_10_act)
        self.menu.addAction(frame_15_act)
        self.menu.addAction(frame_20_act)
        self.menu.addAction(frame_25_act)

        self.menu.addAction(QAction(QIcon(), 'User defined...', self))
        self.menu.addSeparator()

        actionLoop = QAction(QIcon(), 'Loop', self, checkable=True)
        actionLoop.triggered.connect(self.loopChanged)
        self.menu.addAction(actionLoop)

        self.setMenu(self.menu)

    def state(self):
        return self._state

    @pyqtSlot()
    def stateChanged(self):
        if self._state is True:
            self._state = False
            self.setIcon(QIcon(':/icons/pause.png'))
        else:
            self._state = True
            self.setIcon(QIcon(':/icons/play.png'))

    def loop(self):
        return self._loop

    @pyqtSlot(bool)
    def loopChanged(self, loop):
        self._loop = loop

    def framesPerSecond(self):
        return self._frames_per_second

    @pyqtSlot(QAction)
    def framesPerSecondChanded(self, action):
        self._frames_per_second = action.data()
