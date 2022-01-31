import numpy

from pydicom import read_file

from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QDate, pyqtSlot, Qt
from PyQt5.QtWidgets import QWidget, QFileDialog

from libcore import dicom
from libcore.display import PolyActor
from libcore.mesh import Mesh

from ..models.image import imageModel
from ..models.stage import stageModel
from ..models.editor import editorModel

from .dicomdatabasedialog import DICOMDatabaseDialog

from ..views.patientcard_ui import Ui_PatientCard

from app import resources_rc


class PatientCard(QWidget, Ui_PatientCard):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)

        self._photo = None
        self._card = {"name": "",
                      "sex": "М",
                      "birthdate": "1900.01.30",
                      "weight": 0.0}
        self._vti = None

        self.pbNext.setEnabled(False)

        self.widgetSlices.setSlices([])
        self.on_dateTimeEditBirthdate_dateChanged(QDate.fromString(self._card['birthdate'],
                                                                   'yyyy.MM.dd'))

        self.labelPhoto.setPixmap(QPixmap(':/icons/photo2.jpg').scaled(200, 200, Qt.KeepAspectRatio))

        self.labelPreview.setPixmap(QPixmap(':/icons/photo2.jpg').scaled(300, 300, Qt.KeepAspectRatio))

        self.imageModel = imageModel
        self.stageModel = stageModel
        self.editorModel = editorModel

    @pyqtSlot(QDate)
    def on_dateTimeEditBirthdate_dateChanged(self, born):
        today = QDate().currentDate()
        age = today.year() - born.year() - ((today.month(), today.day())
                                            < (born.month(), born.day()))
        self.lineEditAge.setText(str(age))

    @pyqtSlot()
    def on_pushButtonPhoto_pressed(self):
        fileName, _ = QFileDialog.getOpenFileName(self,
                                                  "Выбор фотографии пациента",
                                                  "",
                                                  "JPEG (*.JPEG *.jpeg *.JPG *.jpg *.JPE *.jpe *JFIF *.jfif);; PNG (*.PNG *.png)")
        if fileName:
            self._photo = fileName
            self.labelPhoto.setPixmap(
                QPixmap(self._photo).scaled(200, 200, Qt.KeepAspectRatio))

    def on_pushButtonDICOM_pressed(self):
        log = open('C:/Users/Public/Documents/log_file.txt', 'a')
        log.write('Загрузка DICOM файла'+'\n')
        log.close()
        self.ddd = DICOMDatabaseDialog(self)
        self.ddd.slices.connect(self.setSlices)
        self.ddd.preview.connect(self.setPreview)
        self.ddd.show()

    def on_pushButtonSTL_pressed(self):
        log = open('C:/Users/Public/Documents/log_file.txt', 'a')
        log.write('Загрузка STL файла'+'\n')
        log.close()
        file_name, _ = QFileDialog.getOpenFileName(self,
                                                   "Открыть STL",
                                                   "",
                                                   "Файлы STL (*.stl)")
        if file_name:
            self.editorModel.addProp('mesh', PolyActor(Mesh(file_name)))
            self.stageModel.stage = 3

    @pyqtSlot(list)
    def setSlices(self, slices):
        metadata = dicom.read_metadata(slices[0])
        if str(metadata['patient_name']) == 'PETUHOVA_T_A':
            self.stageModel.name = 'PETUHOVA_T_A'

        if self.lineEditName.text() == "":
            self.lineEditName.setText(str(metadata['patient_name']))
        if metadata['patient_sex'] == "F":
            self.comboBoxSex.setCurrentIndex(1)
        else:
            self.comboBoxSex.setCurrentIndex(0)
        pbd = str(metadata['patient_birth_date'])
        if pbd:
            qbd = QDate(int(pbd[:4]), int(pbd[4:6]), int(pbd[6:8]))
        else:
            qbd = QDate(1900, 1, 30)
        if self.dateTimeEditBirthdate.date() == QDate.fromString('1900.01.30', 'yyyy.MM.dd'):
            self.dateTimeEditBirthdate.setDate(qbd)

        self.widgetSlices.setSlices(slices)
        self._vti = dicom.read_volume(slices)
        self.imageModel.setImage(self._vti)

        self.pbNext.setEnabled(True)

    @pyqtSlot(numpy.ndarray)
    def setPreview(self, preview):
        if preview is not None:
            height, width, channel = preview.shape
            bytesPerLine = 3 * width
            qPix = QPixmap(QImage(preview.data,
                                  width,
                                  height,
                                  bytesPerLine,
                                  QImage.Format_RGB888)).scaled(300,
                                                                300,
                                                                Qt.KeepAspectRatio)
        else:
            qPix = QPixmap(QImage(':/icons/photo2.jpg')).scaled(300,
                                                               300,
                                                               Qt.KeepAspectRatio)
        self.labelPreview.setPixmap(qPix)

    def on_pbNext_pressed(self):
        log = open('C:/Users/Public/Documents/log_file.txt', 'a')
        log.write('Начало работы с моделью'+'\n')
        log.close()
        self.stageModel.stage = 1
