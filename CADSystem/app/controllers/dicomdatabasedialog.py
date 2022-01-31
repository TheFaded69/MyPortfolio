import os
import io
import vtk
import numpy
import pydicom
import sqlite3

from pathlib import Path
from functools import partial

from PyQt5.QtGui import QPixmap, QIcon, QImage
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QThread, Qt, QEvent
from PyQt5.QtWidgets import QDialog, QFileDialog, QProgressDialog, QLabel, QTableWidgetItem, QListWidgetItem, QHeaderView, QPushButton

from libcore import dicom
from libcore.dicom import pydicom_type_to_python
from libcore.image import Image
from libcore.display import VolActor

from ..models.image import imageModel

from ..views.dicomdatabasedialog_ui import Ui_DICOMDatabaseDialog


# хранение базы данных
if os.getenv('APPDATA'):
    if not os.path.exists(os.getenv('APPDATA') + '/cadsi/'):
        os.makedirs(os.getenv('APPDATA') + '/cadsi/')

    DATABASE_PATH = os.getenv('APPDATA') + '/cadsi/dicom.db'
else:
    DATABASE_PATH = 'dicom.db'


def adapt_array(arr):
    """
    http://stackoverflow.com/a/31312102/190597 (SoulNibbler)
    """
    out = io.BytesIO()
    numpy.save(out, arr)
    out.seek(0)
    return sqlite3.Binary(out.read())


def convert_array(text):
    out = io.BytesIO(text)
    out.seek(0)
    return numpy.load(out)


# Converts np.array to TEXT when inserting
sqlite3.register_adapter(numpy.ndarray, adapt_array)
# Converts TEXT to np.array when selecting
sqlite3.register_converter("array", convert_array)


class DICOMDatabaseDialog(QDialog, Ui_DICOMDatabaseDialog):
    slices = pyqtSignal(list)
    preview = pyqtSignal(numpy.ndarray)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)

        self.setWindowFlags(
            self.windowFlags() | Qt.WindowMaximizeButtonHint | Qt.WindowMinimizeButtonHint)

        self.tableWidgetPatients.selectionModel().clearSelection()

        self._patient_uid = None
        self._series_instance_uid = None

        self._conn = sqlite3.connect(DATABASE_PATH,
                                     detect_types=sqlite3.PARSE_DECLTYPES)

        self._cur = self._conn.cursor()
        self._cur.execute('PRAGMA foreign_keys = ON')
        self._cur.execute(sql_create_patients_table)
        self._cur.execute(sql_create_series_table)
        self._cur.execute(sql_create_slices_table)

        self.updatePatients()
        self.updateSeries()
        self.updateSlices()

    def deleteNonSlices(self):
        rows = []
        for row in self._cur.execute('SELECT * FROM slices GROUP BY series_instance_uid'):
            if not os.path.isfile(row[0]):
                rows.append(row)
        for row in rows:
            self._cur.execute('DELETE FROM series WHERE series_instance_uid = ?',
                              (row[1],))

        self._conn.commit()

        if len(rows) > 0:
            self.updatePatients()
            self.updateSeries()
            self.updateSlices()

    def updatePatients(self):
        self.tableWidgetPatients.setRowCount(0)

        for row, patient in enumerate(self._cur.execute("SELECT * FROM patients")):
            self.tableWidgetPatients.insertRow(
                self.tableWidgetPatients.rowCount())
            for col, item in enumerate(patient):
                if col == 0:
                    patient_uid = item
                    continue
                if col == 4:
                    for ch in (("F", "Ж"), ("M", "М")):
                        item = item.replace(ch[0], ch[1])
                if col == 5:
                    pbd = str(item)
                    item = pbd[:4] + "/" + pbd[4:6] + "/" + pbd[6:8]

                item = QTableWidgetItem(str(item))
                self.tableWidgetPatients.setItem(row, col - 1, item)

                if col == 1:
                    item.setData(Qt.UserRole, patient_uid)

            cur = self._conn.cursor()
            r = cur.execute("""
                                SELECT COUNT(*)
                                FROM slices
                                JOIN series ON series.series_instance_uid = slices.series_instance_uid
                                WHERE series.patient_uid = ?
                            """, (patient_uid,))
            cnt = r.fetchone()[0]

            if cnt == 0:
                cur.execute(
                    "DELETE FROM patients WHERE patient_uid = ?", (patient_uid, ))
                self._conn.commit()
                self.updatePatients()

            item = QTableWidgetItem(str(cnt))
            self.tableWidgetPatients.setItem(row, col, item)

            btn = QPushButton()
            btn.pressed.connect(
                partial(self.deletePatient, patient_uid=patient_uid))
            btn.setIcon(QIcon(QPixmap(":/icons/delete.png")))
            self.tableWidgetPatients.setCellWidget(row, 7, btn)

        self.tableWidgetPatients.resizeColumnsToContents()
        self.tableWidgetPatients.resizeRowsToContents()
        self.tableWidgetPatients.horizontalHeader().setSectionResizeMode(5,
                                                                         QHeaderView.Stretch)

    def updateSeries(self):
        self.listWidgetSeries.clear()

        if self._patient_uid == None:
            return

        query = 'SELECT * FROM series WHERE patient_uid = ' + \
            str(self._patient_uid)

        for row, serie in enumerate(self._cur.execute(query)):
            item = QListWidgetItem(str(serie[4]))
            item.setData(Qt.UserRole, serie[0])
            icon = QIcon()

            if serie[7] is not None:
                height, width, channel = serie[7].shape
                bytesPerLine = 3 * width
                qImg = QImage(serie[7].data, width, height,
                              bytesPerLine, QImage.Format_RGB888)
            else:
                qImg = QImage('D:/Projects/CADSystem/cadsi/resources/icons/photo2.jpg')
            icon.addPixmap(QPixmap(qImg),
                           QIcon.Normal, QIcon.Off)
            item.setIcon(icon)
            ttip = "<b>Модальность:</b> " + serie[5] + "<br>" + \
                "<b>Дата:</b> " + serie[2][:4] + "-" + serie[2][4:6] + "-" + serie[2][6:8] + "<br>" + \
                "<b>Время:</b> " + serie[3][:2] + ":" + serie[3][2:4] + ":" + serie[2][4:6] + "<br>" + \
                "<b>Учреждение:</b> " + serie[6] + "<br>" + \
                "<b>Комментарии:</b> " + serie[4] + "<br>"
            item.setToolTip(ttip)
            self.listWidgetSeries.addItem(item)

    def updateSlices(self):
        self.deleteNonSlices()

        if self._series_instance_uid == None:
            self.widgetSlices.setSlices([])
            return

        self._cur.execute('SELECT slice_path FROM slices WHERE series_instance_uid = ?',
                          (self._series_instance_uid, ))
        self.widgetSlices.setSlices([x[0] for x in self._cur.fetchall()])

    @pyqtSlot(int)
    def deletePatient(self, patient_uid):
        self._cur.execute('DELETE FROM patients WHERE patient_uid = ?',
                          (patient_uid, ))
        self._conn.commit()

        self._patient_uid = None
        self._series_instance_uid = None

        self.updatePatients()
        self.updateSeries()
        self.updateSlices()

    @pyqtSlot(int, int)
    def on_tableWidgetPatients_cellClicked(self, row, column):
        patient_uid = self.tableWidgetPatients.item(row,
                                                    0).data(Qt.UserRole)
        if patient_uid == self._patient_uid:
            self.tableWidgetPatients.selectionModel().clearSelection()
            self._patient_uid = None
        else:
            self._patient_uid = patient_uid

        self._series_instance_uid = None

        self.updateSeries()
        self.updateSlices()

    @pyqtSlot(QListWidgetItem)
    def on_listWidgetSeries_itemClicked(self, item):
        series_instance_uid = item.data(Qt.UserRole)

        if series_instance_uid == self._series_instance_uid:
            self.listWidgetSeries.selectionModel().clearSelection()
            self._series_instance_uid = None
            self.pushButtonImport.setEnabled(False)
        else:
            self.pushButtonImport.setEnabled(True)
            self._series_instance_uid = series_instance_uid

        self.updateSlices()

    @pyqtSlot(QListWidgetItem)
    def on_listWidgetSeries_itemDoubleClicked(self, item):
        self._series_instance_uid = item.data(Qt.UserRole)
        self.on_pushButtonImport_pressed()

    @pyqtSlot()
    def on_pushButtonScan_pressed(self):
        log = open('C:/Users/Public/Documents/log_file.txt','a')
        log.write('Сканирование DICOM файлов'+'\n')
        log.close()
        dir_name = str(QFileDialog.getExistingDirectory(self,
                                                        'Открыть',
                                                        str(Path.home()),
                                                        QFileDialog.ShowDirsOnly))

        if dir_name:
            pd = QProgressDialog(self)
            pd.setMinimum(0)
            pd.setMaximum(0)
            pd.setValue(0)
            pd.resize(400, 100)
            pd.setLabel(QLabel("Чтение DICOM файлов...", pd))
            pd.show()

            thread = UpdateDatabase(self, dir_name)
            thread.finished.connect(pd.close)
            thread.finished.connect(self.updatePatients)
            thread.finished.connect(self.updateSeries)
            thread.finished.connect(self.updateSlices)
            thread.start()

    @pyqtSlot()
    def on_pushButtonImport_pressed(self):
        log = open('C:/Users/Public/Documents/log_file.txt','a')
        log.write('Импорт DICOM файла в КАД систему'+'\n')
        log.close()
        if self._series_instance_uid:
            self._cur.execute('SELECT slice_path FROM slices WHERE series_instance_uid = ?',
                              (self._series_instance_uid, ))
            slices = [x[0] for x in self._cur.fetchall()]
            self.slices.emit(slices)

            imageModel.uid = self._series_instance_uid

            self._cur.execute('SELECT series_preview FROM series WHERE series_instance_uid = ?',
                              (self._series_instance_uid,))
            self.preview.emit(self._cur.fetchone()[0])

            self.close()

sql_create_patients_table = """ CREATE TABLE IF NOT EXISTS patients (
  patient_uid INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
  patient_name VARCHAR(255) NULL,
  patient_age VARCHAR(255) NULL,
  patient_id VARCHAR(255) NULL,
  patient_sex VARCHAR(255) NULL,
  patient_birth_date VARCHAR(255) NULL,
  patient_comments VARCHAR(255) NULL,
  UNIQUE(patient_name, patient_age, patient_id, patient_sex, patient_birth_date, patient_comments) ON CONFLICT IGNORE
  )
"""

sql_create_series_table = """ CREATE TABLE IF NOT EXISTS series (
  series_instance_uid VARCHAR(255) NOT NULL,
  series_number VARCHAR(255) NULL,
  series_date VARCHAR(255) NULL,
  series_time VARCHAR(255) NULL,
  series_description VARCHAR(255) NULL,
  modality VARCHAR(255) NULL,
  institution_name VARCHAR(255) NULL,
  series_preview array NULL,
  patient_uid INTEGER NOT NULL,
  PRIMARY KEY (series_instance_uid),
  FOREIGN KEY (patient_uid) REFERENCES patients(patient_uid) ON DELETE CASCADE
  )
"""

sql_create_slices_table = """ CREATE TABLE IF NOT EXISTS slices (
  slice_path TEXT NOT NULL,
  series_instance_uid VARCHAR(255) NOT NULL,
  UNIQUE(slice_path) ON CONFLICT IGNORE,
  FOREIGN KEY (series_instance_uid) REFERENCES series(series_instance_uid) ON DELETE CASCADE
  )
"""


class UpdateDatabase(QThread):

    def __init__(self, parent, directory):
        super().__init__(parent)
        self.directory = directory

    def run(self):
        conn = sqlite3.connect(DATABASE_PATH,
                               detect_types=sqlite3.PARSE_DECLTYPES)
        cur = conn.cursor()

        patient_fields = [col[1] for col in cur.execute(
            "PRAGMA table_info('patients')") if col[1] not in ['patient_uid']]
        serie_fields = [col[1] for col in cur.execute(
            "PRAGMA table_info('series')") if col[1] not in []]

        # sql
        sql_select_from_patients = 'SELECT patient_uid FROM patients WHERE ' + \
            ' = ? AND '.join(patient_fields) + ' = ?'
        sql_insert_into_patients = 'INSERT INTO patients(' + ', '.join(
            patient_fields) + ') VALUES(' + ', '.join(['?'] * len(patient_fields)) + ')'
        sql_insert_into_series = 'INSERT INTO series(' + ', '.join(
            serie_fields) + ') VALUES(' + ', '.join(['?'] * len(serie_fields)) + ')'

        series_raw = dicom.scan_directory(self.directory)

        series = []
        for item in series_raw.items():
            slice_path = item[0]
            serie_raw = item[1]

            series_instance_uid = serie_raw.get('series_instance_uid')
            if not series_instance_uid:
                continue
            if series_instance_uid not in series:
                series.append(series_instance_uid)

            # patient to db
            patient = tuple(
                map(lambda x: str(serie_raw.get(x, '')), patient_fields))
            cur.execute(sql_select_from_patients, patient)
            try:
                serie_raw['patient_uid'] = cur.fetchone()[0]
            except TypeError:
                cur.execute(sql_insert_into_patients, patient)
                serie_raw['patient_uid'] = cur.lastrowid

            # serie to db

            serie = tuple(
                map(lambda x: str(serie_raw.get(x, '')), serie_fields))
            cur.execute(
                'SELECT * FROM series WHERE series_instance_uid = ?', (series_instance_uid, ))
            if cur.fetchone() is None:
                cur.execute(sql_insert_into_series, serie)

            # slice to db
            cur.execute(
                'INSERT INTO slices(slice_path, series_instance_uid) VALUES(?, ?)', (slice_path, series_instance_uid))

        conn.commit()

        renderer = vtk.vtkRenderer()
        render_window = vtk.vtkRenderWindow()
        render_window.SetOffScreenRendering(1)
        render_window.AddRenderer(renderer)
        render_window.SetSize(512, 512)

        camera = renderer.GetActiveCamera()
        camera.SetPosition(0, -1.0, 0)
        camera.SetFocalPoint(0, 0.0, 0)

        # сортировка слайсов и добавление изображения
        for series_instance_uid in series:
            cur.execute('SELECT slice_path FROM slices WHERE series_instance_uid = ?',
                        (series_instance_uid, ))
            slices = dicom.sort_files([x[0] for x in cur.fetchall()])
            cur.execute('DELETE FROM slices WHERE series_instance_uid = ?',
                        (series_instance_uid, ))
            for slice_path in slices:
                cur.execute('INSERT INTO slices(slice_path, series_instance_uid) VALUES(?, ?)',
                            (slice_path, series_instance_uid))

            if len(slices) > 10:
                image = dicom.read_volume(slices)
                actor = VolActor(image)

                renderer.AddActor(actor)
                renderer.ResetCamera()
                camera.Zoom(1.5)
                camera.Roll(180)
                render_window.Render()

                window_to_image_filter = vtk.vtkWindowToImageFilter()
                window_to_image_filter.SetInput(render_window)
                window_to_image_filter.Update()

                renderer.RemoveActor(actor)

                result = Image(window_to_image_filter.GetOutput())
                series_preview = numpy.fliplr(result.as_numpy())

                cur.execute('UPDATE series SET series_preview = ? WHERE series_instance_uid = ?',
                            (series_preview, series_instance_uid,))

        conn.commit()
        conn.close()
