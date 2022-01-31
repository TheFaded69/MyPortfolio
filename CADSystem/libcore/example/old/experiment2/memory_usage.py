import os
import time
import psutil

from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QStatusBar


class StatusBar(QStatusBar):

    def init(self, parent=None):
        super().init(parent=parent)

        process = psutil.Process(os.getpid())
        thread = StatusBar.ShowUsage(self, process)
        thread.start()

    class ShowUsage(QThread):

        def init(self, parent, process):
            super().init(parent=parent)
            self.parent = parent
            self.process = process

        def run(self):
            count = 0
            if count < 100:
                print(count)
                self.parent.showMessage('{} ЦП: {:.2}% Память: {:.2}%'.format(count,
                                                                              self.process.cpu_percent(),
                                                                              self.process.memory_percent()))
                time.sleep(1)
                count += 1