from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import QWidget, QTableWidgetItem, QHeaderView

from pydicom import read_file

from libcore.dicom import pydicom_type_to_python

from ..views.slicemetadata_ui import Ui_SliceMetadata


class SliceMetadata(QWidget, Ui_SliceMetadata):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)

        self._slices = []

    def setSlices(self, slices):
        self._slices = slices
        if self._slices == []:
            self.spinBox.setMaximum(0)
            self.horizontalSlider.setMaximum(0)
            self.setEnabled(False)
        else:
            self.spinBox.setMaximum(len(self._slices) - 1)
            self.horizontalSlider.setMaximum(len(self._slices) - 1)
            self.setEnabled(True)

        self.updateTable(0)

    @pyqtSlot(int)
    def updateTable(self, idx):
        self.tableWidget.setRowCount(0)
        self.label.setText("Путь к файлу")

        if self.spinBox.value() != idx:
            self.spinBox.setValue(idx)
        if self.horizontalSlider.value() != idx:
            self.horizontalSlider.setValue(idx)

        try:
            slice = self._slices[idx]
        except IndexError:
            return

        self.label.setText(slice)

        ds = read_file(slice, stop_before_pixels=True)
        for row, data in enumerate(ds):
            self.tableWidget.insertRow(self.tableWidget.rowCount())
            item = QTableWidgetItem(str(data.tag))
            self.tableWidget.setItem(row, 0, item)
            item = QTableWidgetItem(str(data.name))
            self.tableWidget.setItem(row, 1, item)
            if isinstance(data.value, bytes):
                data_value = str(data.value.decode("utf-8", "ignore")).strip()
            else:
                data_value = str(data.value)
            item = QTableWidgetItem(data_value)
            self.tableWidget.setItem(row, 2, item)
            item = QTableWidgetItem(str(data.VR))
            self.tableWidget.setItem(row, 3, item)

        self.tableWidget.resizeRowsToContents()
        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.horizontalHeader().setSectionResizeMode(2,
                                                                 QHeaderView.Stretch)

    @pyqtSlot(int)
    def on_spinBox_valueChanged(self, val):
        self.updateTable(val)

    @pyqtSlot(int)
    def on_horizontalSlider_valueChanged(self, val):
        self.updateTable(val)
