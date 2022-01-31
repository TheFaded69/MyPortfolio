import os
import psutil

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QStatusBar


class StatusBar(QStatusBar):

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.process = psutil.Process(os.getpid())

        self.tmr = QTimer()
        self.tmr.setInterval(1000)
        self.tmr.timeout.connect(self.updateUsage)
        self.tmr.start()

    def updateUsage(self):
        cpu = round(self.process.cpu_percent(), 2)
        memory = round(self.process.memory_percent(), 2)
        self.showMessage('ЦП: {}% Память: {}%'.format(cpu, memory))
