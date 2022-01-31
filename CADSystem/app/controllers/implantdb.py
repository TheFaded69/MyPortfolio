import os
import vtk
import tempfile

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QWidget

from libcore.mesh import Mesh
from libcore.display import PolyActor
from libcore.image import Image

from ..views.implantdatabase_ui import Ui_ImplantDatabase


tmpdir = tempfile.gettempdir()


class ImplantDatabase(QWidget, Ui_ImplantDatabase):
    implant = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)

        self._directory = "./libcore/data/implants"
        self.listDir()

    def listDir(self):
        for root, dirs, files in os.walk(self._directory):
            for file in files:
                if file[-3:].lower() == 'stl':
                    print(root, file)
                    icon = screenshot(root + '/' + file)

                    # Create QCustomQWidget
                    myQCustomQWidget = QCustomQWidget()
                    myQCustomQWidget.setTextUp(file)
                    myQCustomQWidget.setTextDown(root + '/' + file)
                    myQCustomQWidget.setIcon(icon)
                    # Create QListWidgetItem
                    listWidgetItem = QtWidgets.QListWidgetItem(self.listWidget)
                    # Set size hint
                    listWidgetItem.setSizeHint(myQCustomQWidget.sizeHint())
                    # Add QListWidgetItem into QListWidget
                    self.listWidget.addItem(listWidgetItem)
                    self.listWidget.setItemWidget(listWidgetItem,
                                                  myQCustomQWidget)

    @pyqtSlot(QtWidgets.QListWidgetItem)
    def on_listWidget_itemDoubleClicked(self, item):
        file_path = self.listWidget.itemWidget(item).textDownQLabel.text()
        if os.path.exists(tmpdir + '/tmp.stl'):
            os.remove(tmpdir + '/tmp.stl')
        os.link(file_path, tmpdir + '/tmp.stl')
        self.implant.emit(tmpdir + '/tmp.stl')


class QCustomQWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(QCustomQWidget, self).__init__(parent)
        self.textQVBoxLayout = QtWidgets.QVBoxLayout()
        self.textUpQLabel = QtWidgets.QLabel()
        self.textDownQLabel = QtWidgets.QLabel()
        self.textQVBoxLayout.addWidget(self.textUpQLabel)
        self.textQVBoxLayout.addWidget(self.textDownQLabel)
        self.allQHBoxLayout = QtWidgets.QHBoxLayout()
        self.iconQLabel = QtWidgets.QLabel()
        self.iconQLabel.setMaximumSize(50, 50)
        self.allQHBoxLayout.addWidget(self.iconQLabel, 0)
        self.allQHBoxLayout.addLayout(self.textQVBoxLayout, 1)
        self.setLayout(self.allQHBoxLayout)
        # setStyleSheet
        # self.textUpQLabel.setStyleSheet('''
        #     color: rgb(0, 0, 255);
        # ''')
        # self.textDownQLabel.setStyleSheet('''
        #     color: rgb(255, 0, 0);
        # ''')

    def setTextUp(self, text):
        self.textUpQLabel.setText(text)

    def setTextDown(self, text):
        self.textDownQLabel.setText(text)

    def setIcon(self, imagePath):
        height, width, channel = imagePath.shape
        bytesPerLine = 3 * width
        qImg = QtGui.QImage(imagePath.data,
                            width,
                            height,
                            bytesPerLine,
                            QtGui.QImage.Format_RGB888)

        self.iconQLabel.setPixmap(QtGui.QPixmap(qImg).scaled(50, 50))


renderer = vtk.vtkRenderer()
render_window = vtk.vtkRenderWindow()
render_window.SetOffScreenRendering(1)
render_window.AddRenderer(renderer)
render_window.SetSize(512, 512)
camera = renderer.GetActiveCamera()
camera.SetPosition(0, -1.0, 0)
camera.SetFocalPoint(0, 0.0, 0)
camera.Zoom(1.5)
camera.Roll(180)


def screenshot(file_path):
    if os.path.exists(tmpdir + '/tmp.stl'):
        os.remove(tmpdir + '/tmp.stl')
    os.link(file_path, tmpdir + '/tmp.stl')
    image = Mesh(tmpdir + '/tmp.stl')
    # image = Mesh('./implants/Пластины/PBL-102.stl')
    actor = PolyActor(image)

    renderer.AddActor(actor)
    renderer.ResetCamera()
    render_window.Render()

    window_to_image_filter = vtk.vtkWindowToImageFilter()
    window_to_image_filter.SetInput(render_window)
    window_to_image_filter.Update()

    renderer.RemoveActor(actor)

    result = Image(window_to_image_filter.GetOutput())
    return result.as_numpy()

if __name__ == "__main__":
    import os
    import sys

    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)

    mw = ImplantDatabase()
    mw.showMaximized()

    sys.exit(app.exec_())
