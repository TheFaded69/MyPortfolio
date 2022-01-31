from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QWidget

from ..models.look import LookModel, lookModel

from ..views.look_ui import Ui_Look
#from app.__main__ import log

class Look(QWidget, Ui_Look):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)

        self.lookModel = lookModel

    @pyqtSlot()
    def on_toolButtonAP_pressed(self):
        self.lookModel.setLook(LookModel.AP)
        log = open('C:/Users/Public/Documents/log_file.txt','a')
        log.write('Выбран вид спереди'+'\n')
        log.close()

    @pyqtSlot()
    def on_toolButtonPA_pressed(self):
        self.lookModel.setLook(LookModel.PA)
        log = open('C:/Users/Public/Documents/log_file.txt','a')
        log.write('Выбран вид сзади'+'\n')
        log.close()

    @pyqtSlot()
    def on_toolButtonLAO_pressed(self):
        self.lookModel.setLook(LookModel.LAO)
        log = open('C:/Users/Public/Documents/log_file.txt','a')
        log.write('Выбран левый передний косой вид'+'\n')
        log.close()

    @pyqtSlot()
    def on_toolButtonRAO_pressed(self):
        self.lookModel.setLook(LookModel.RAO)
        log = open('C:/Users/Public/Documents/log_file.txt','a')
        log.write('Выбран правый передний косой вид'+'\n')
        log.close()

    @pyqtSlot()
    def on_toolButtonSUP_pressed(self):
        self.lookModel.setLook(LookModel.SUP)
        log = open('C:/Users/Public/Documents/log_file.txt','a')
        log.write('Выбран вид сверху'+'\n')
        log.close()

    @pyqtSlot()
    def on_toolButtonINF_pressed(self):
        self.lookModel.setLook(LookModel.INF)
        log = open('C:/Users/Public/Documents/log_file.txt','a')
        log.write('Выбран вид снизу'+'\n')
        log.close()

    @pyqtSlot()
    def on_toolButtonLL_pressed(self):
        self.lookModel.setLook(LookModel.LL)
        log = open('C:/Users/Public/Documents/log_file.txt','a')
        log.write('Выбран вид слева'+'\n')
        log.close()

    @pyqtSlot()
    def on_toolButtonRL_pressed(self):
        self.lookModel.setLook(LookModel.RL)
        log = open('C:/Users/Public/Documents/log_file.txt','a')
        log.write('Выбран вид справа'+'\n')
        log.close()
