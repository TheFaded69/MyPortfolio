import sys
import vtk
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication

from libcore.mesh import Mesh
from libcore.mesh import transform
from libcore.display import PolyActor
from libcore.qt import Viewport
from libcore.interact import StyleDrawPolygon
from libcore.widget import PlaneSelector
from libcore.geometry import Plane

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
        self.btn_split = QtWidgets.QPushButton("Split")
        self.btn_split.clicked.connect(self.split)
        self.btn_save_red = QtWidgets.QPushButton("Save red")
        self.btn_save_red.clicked.connect(self.save_red)
        self.btn_save_green = QtWidgets.QPushButton("Save green")
        self.btn_save_green.clicked.connect(self.save_green)

        self.tools = QtWidgets.QVBoxLayout(self)
        self.tools.addWidget(self.btn_load)
        self.tools.addWidget(self.btn_split)
        self.tools.addWidget(self.btn_save_red)
        self.tools.addWidget(self.btn_save_green)
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
            self.actor = self.view.add_prop(PolyActor(self.mesh, color='white', opacity=1.0))
            self.plane = PlaneSelector(self.view.interactor, Plane(origin=self.mesh.center, normal=(1, 0, 0)), self.mesh.bounds)
            self.plane.show()
            self.view.reset_view()

    def split(self):
        self.red, self.green = self.mesh.disect_by_plane(self.plane.plane)
        print(self.red)
        print(self.green)
        print('close red mesh')
        self.red.close_mesh(inplace=True)
        print('close green mesh')
        self.green.close_mesh(inplace=True)
        print('hide actor')
        #self.actor.hide()
        print('hide plane')
        self.plane.hide()
        print('add prop for red mesh')

        self.red = transform(self.red, ttype='reflect')
        self.view.add_prop(PolyActor(self.red, color='red'))
        print('add prop for green mesh')
        self.view.add_prop(PolyActor(self.green, color='green'))
        print('reset view view')
        self.view.reset_view()



    def save_red(self):
        name, _ = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File')
        self.red.save(name)


    def save_green(self):
        name, _ = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File')
        self.green.save(name)
        print('green')


    def on_select_handler(self, selection):
        self.mesh.clip_by_mesh(selection, True, inplace=True)
        self.view.rwindow.Render()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SimpleView()
    window.show()
    window.view.interactor.Initialize()
    sys.exit(app.exec_())