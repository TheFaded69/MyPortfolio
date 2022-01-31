import os
import vtk

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QWidget, QFileDialog

from libcore.qt import Viewport
from libcore.display import PolyActor
from libcore.mesh import Mesh

from ..models.printer import printerModel
from ..models.look import lookModel
from ..models.image import imageModel

from ..views.printer_ui import Ui_Printer
from time import gmtime, strftime


class Printer(QWidget, Ui_Printer):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
        self.viewport = Viewport()
        self.viewport.istyle = vtk.vtkInteractorStyleTrackballCamera()
        self.viewport.interactor.Initialize()
        self.layout.addWidget(self.viewport)

        self.lookModel = lookModel
        self.lookModel.lookUpdated.connect(self.updateLook)

        self.printerModel = printerModel
        self.printerModel.loaded.connect(self.loadMesh)

        self.imageModel = imageModel

    @pyqtSlot(tuple)
    def updateLook(self, look):
        self.viewport.look_from(look)

    def loadMesh(self):
        if hasattr(self, 'actor_implant'):
            self.viewport.remove_prop(self.actor_implant)
        if hasattr(self, 'actor_cylinders'):
            self.viewport.remove_prop(self.actor_cylinders)

        if self.printerModel.implant:
            self.implant = Mesh(self.printerModel.implant)
            self.actor_implant = PolyActor(self.implant, color="white")
            self.viewport.add_prop(self.actor_implant)

            self.cylinders = Mesh(self.printerModel.cylinders)
            self.actor_cylinders = PolyActor(self.cylinders, color="green")
            self.viewport.add_prop(self.actor_cylinders)

            self.viewport.reset_view()
            self.label.setText("Объем: {:.2f} см³".format(estimate_volume(self.implant) / 1000.0))

    def saveScreenshot(self, file_name):
        if file_name:
            w2if = vtk.vtkWindowToImageFilter()
            w2if.SetInput(self.viewport.rwindow)
            w2if.Update()

            writer = vtk.vtkPNGWriter()
            writer.SetFileName(file_name + '.png')
            writer.SetInputData(w2if.GetOutput())
            writer.Write()

    def saveScreenshots(self, file_name):
        if file_name:
            self.viewport.look_pa()
            self.saveScreenshot(file_name + '_PA')
            self.viewport.look_lao()
            self.saveScreenshot(file_name + '_LAO')
            self.viewport.look_rao()
            self.saveScreenshot(file_name + '_RAO')
            self.viewport.look_sup()
            self.saveScreenshot(file_name + '_SUP')
            self.viewport.look_inf()
            self.saveScreenshot(file_name + '_INF')
            self.viewport.look_ll()
            self.saveScreenshot(file_name + '_LL')
            self.viewport.look_rl()
            self.saveScreenshot(file_name + '_RL')
            self.viewport.look_ap()
            self.saveScreenshot(file_name + '_AP')

    def on_pbPrtSc_pressed(self):
        log = open('C:/Users/Public/Documents/log_file.txt', 'a')
        log.write('Сохранить скриншот'+'\n')
        log.close()
        file_name, _ = QFileDialog.getSaveFileName(self,
                                                   "Сохранить PNG",
                                                   "",
                                                   "Файлы PNG (*.png)")

        if file_name:
            w2if = vtk.vtkWindowToImageFilter()
            w2if.SetInput(self.viewport.rwindow)
            w2if.Update()

            writer = vtk.vtkPNGWriter()
            writer.SetFileName(file_name)
            writer.SetInputData(w2if.GetOutput())
            writer.Write()

    def on_pbFix_pressed(self):
        log = open('C:/Users/Public/Documents/log_file.txt', 'a')
        log.write('Починить имплант'+'\n')
        log.close()
        self.implant.clean()
        self.viewport.rwindow.Render()

    def on_pbSaveDICOM_pressed(self):
        log = open('C:/Users/Public/Documents/log_file.txt', 'a')
        log.write('Сохранить файл DICOM'+'\n')
        log.close()
        file_name, _ = QFileDialog.getSaveFileName(self,
                                                   "Сохранить DICOM",
                                                   "",
                                                   "Файлы DICOM (*.dicom)")
        if file_name:
            self.implant.save(file_name + '.stl')
            self.cylinders.save(file_name + '-cylinders.stl')
            os.rename(file_name + '.stl', file_name)
            print(file_name)
            with open(file_name + '.txt', 'w', encoding="utf-8") as f:
                print(self.imageModel.uid, "\n",
                      file_name, "\n",
                      "Объем: {:.2f} см³".format(estimate_volume(self.implant, not bool(self.checkBox.isChecked())) / 1000.0), "\n",
                      strftime("%Y-%m-%d %H:%M:%S", gmtime()), "\n",
                      self.imageModel.image,
                      self.implant,
                      file=f)
            self.saveScreenshots(file_name)

    def on_pbSaveDXF_pressed(self):
        log = open('C:/Users/Public/Documents/log_file.txt', 'a')
        log.write('Сохранить файл DXF'+'\n')
        log.close()
        file_name, _ = QFileDialog.getSaveFileName(self,
                                                   "Сохранить DXF",
                                                   "",
                                                   "Файлы DXF (*.dxf)")
        if file_name:
            self.implant.save(file_name + '.stl')
            self.cylinders.save(file_name + '-cylinders.stl')
            os.rename(file_name + '.stl', file_name)
            print(file_name)
            with open(file_name + '.txt', 'w', encoding="utf-8") as f:
                print(self.imageModel.uid, "\n",
                      file_name, "\n",
                      "Объем: {:.2f} см³".format(estimate_volume(self.implant, not bool(self.checkBox.isChecked())) / 1000.0), "\n",
                      strftime("%Y-%m-%d %H:%M:%S", gmtime()), "\n",
                      self.imageModel.image,
                      self.implant,
                      file=f)
            self.saveScreenshots(file_name)

    def on_pbSave_pressed(self):
        log = open('C:/Users/Public/Documents/log_file.txt', 'a')
        log.write('Сохранить файл STL'+'\n')
        log.close()
        file_name, _ = QFileDialog.getSaveFileName(self,
                                                   "Сохранить STL",
                                                   "",
                                                   "Файлы STL (*.stl)")
        if file_name:
            self.implant.save(file_name)
            self.cylinders.save(file_name + '-cylinders.stl')
            print(file_name)
            with open(file_name + '.txt', 'w', encoding="utf-8") as f:
                print(self.imageModel.uid, "\n",
                      file_name, "\n",
                      "Объем: {:.2f} см³".format(estimate_volume(self.implant, not bool(self.checkBox.isChecked())) / 1000.0), "\n",
                      strftime("%Y-%m-%d %H:%M:%S", gmtime()), "\n",
                      self.imageModel.image,
                      self.implant,
                      file=f)
            self.saveScreenshots(file_name)

    def on_rbHigh_toggled(self, toggle):
        if toggle:
            self.implant = Mesh(self.printerModel.implant)
            self.viewport.rwindow.Render()

    def on_rbMiddle_toggled(self, toggle):
        if toggle:
            self.implant.decimate(algorithm='pro', inplace=True, reduction=0.6)
            self.viewport.rwindow.Render()

    def on_rbLow_toggled(self, toggle):
        if toggle:
            self.implant.decimate(algorithm='pro', inplace=True, reduction=0.3)
            self.viewport.rwindow.Render()

    def on_checkBox_toggled(self, toggle):
        self.label.setText("Объем: {:.2f} см³".format(estimate_volume(self.implant, not bool(toggle)) / 1000.0))


def estimate_volume(mesh, simple=True):
    if simple:
        cmp = vtk.vtkMassProperties()
        cmp.SetInputData(mesh)
        cmp.Update()
        return cmp.GetVolume()
    else:
        delaunay = vtk.vtkDelaunay3D()
        delaunay.SetInputData(mesh)
        delaunay.Update()

        surface_filter = vtk.vtkDataSetSurfaceFilter()
        surface_filter.SetInputData(delaunay.GetOutput())
        surface_filter.Update()

        cmp = vtk.vtkMassProperties()
        cmp.SetInputData(surface_filter.GetOutput())
        cmp.Update()
        return cmp.GetVolume()
