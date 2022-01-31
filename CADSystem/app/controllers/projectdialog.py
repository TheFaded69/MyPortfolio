from PyQt5.QtWidgets import QDialog, QFileDialog

from ..models.project import projectModel

from .mainwindow import MainWindow

from ..views.projectdialog_ui import Ui_ProjectDialog


class ProjectDialog(QDialog, Ui_ProjectDialog):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)

        self.projectModel = projectModel

    def on_pushButtonCreateProject_pressed(self):
        self.showCADSI()

    def on_pushButtonOpenProject_pressed(self):
        fileName, _ = QFileDialog.getOpenFileName(self,
                                                  "Открыть проект",
                                                  "",
                                                  "Файлы проектов (*.cadsi)")
        if fileName:
            print(fileName)
            self.projectModel.load(fileName)
            self.showCADSI()

    def showCADSI(self):
        self.mw = MainWindow()
        self.mw.showMaximized()
        self.close()
