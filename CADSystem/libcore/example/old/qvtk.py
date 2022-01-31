import sys
import vtk
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication

from libcore.mesh import Mesh
from libcore.display import PolyActor
from libcore.qt import Viewport
from libcore.interact import StyleDrawPolygon

class SimpleView(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.mesh = None
        self.central = QtWidgets.QWidget(self)
        self.view = Viewport(self)
        self.view.setMinimumHeight(800)
        self.view.setMinimumWidth(1024)
        self.view.istyle = vtk.vtkInteractorStyleTrackballActor()


        self.btn_load = QtWidgets.QPushButton("Load stl")
        self.btn_load.clicked.connect(self.load_stl)
        self.tools = QtWidgets.QVBoxLayout(self)
        self.tools.addWidget(self.btn_load)
        self.tools.addStretch()


        self.main = QtWidgets.QHBoxLayout(self)
        self.main.addWidget(self.view)
        self.main.addLayout(self.tools)
        self.central.setLayout(self.main)
        self.setCentralWidget(self.central)

    def load_stl(self):
        name = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File')
        name = name[0]
        print(name)
        if name:
            self.mesh = Mesh(name)
            self.view.add_prop(PolyActor(self.mesh, color='red', opacity=0.7))
            self.view.istyle = StyleDrawPolygon(on_select=self.on_select_handler)
            self.view.reset_view()

    def on_select_handler(self, selection):
        self.mesh.clip_by_mesh(selection, True, inplace=True)
        self.view.rwindow.Render()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SimpleView()
    window.show()
    window.view.interactor.Initialize()
    sys.exit(app.exec_())