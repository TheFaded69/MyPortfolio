import time
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QFileDialog, QTreeWidgetItem

from ..views.propstree_ui import Ui_PropsTree

from ..models.editor import editorModel

from libcore.color import colors, get_color
from libcore.mesh import Mesh
import threading

class PropsTree(QWidget, Ui_PropsTree):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)

        self.editorModel = editorModel
        self.editorModel.propSelected.connect(self.selectProp)
        self.editorModel.propsUpdated.connect(self.updateProps)

        self.cbMeshColor.addItems(colors())

        self.selectProp()

    def setModel(self, model):
        self.editorModel = model
        self.editorModel.propSelected.connect(self.selectProp)
        self.editorModel.propsUpdated.connect(self.updateProps)

        self.selectProp()

    def selectProp(self):
        toggle = bool(self.editorModel.prop)
        self.cbMeshColor.setEnabled(toggle)
        self.pbSave.setEnabled(toggle)
        self.pbCopy.setEnabled(toggle)
        self.pbDelete.setEnabled(toggle)

        key = self.editorModel.prop
        if key:
            color_prop = get_color(self.editorModel.props[key].color)
            color_err = 1.0
            color_name = 'white'
            for name, color_val in colors(False):
                err_r = color_val.r - color_prop.r
                if err_r < -0.0:
                    err_r = 10.0
                err_g = color_val.g - color_prop.g
                if err_g < -0.0:
                    err_g = 10.0
                err_b = color_val.b - color_prop.b
                if err_b < -0.0:
                    err_b = 10.0
                err = err_r + err_g + err_b
                if err < color_err:
                    color_err = err
                    color_name = name
            idx = self.cbMeshColor.findText(color_name)
            if idx > -1:
                self.cbMeshColor.setCurrentIndex(idx)

            items = self.tree.findItems(key, Qt.MatchContains)
            if len(items) > 0:
                self.tree.setCurrentItem(items[0])
        else:
            self.tree.selectionModel().clearSelection()

    def updateProps(self):
        self.tree.clear()
        for key in self.editorModel.props:
            item = QTreeWidgetItem([key])
            item.setFlags(item.flags() |
                          Qt.ItemIsUserCheckable |
                          Qt.ItemIsEnabled)
            if self.editorModel.props[key].GetVisibility():
                item.setCheckState(0, Qt.Checked)
            else:
                item.setCheckState(0, Qt.Unchecked)
            self.tree.addTopLevelItem(item)
            if key == self.editorModel.prop:
                self.tree.setCurrentItem(item)

    def on_tree_itemChanged(self, item, column):
        key = item.text(column)
        toggle = item.checkState(column)

        # if key in self.editorModel._props:
        #     if self.editorModel._props[key].is_visible != toggle:
        #         self.editorModel._props[key].SetVisibility(toggle)
        #         self.editorModel.propsUpdated.emit()

        thread1 = threading.Thread(target = thread_tree_itemChanged, args = (self, key, toggle))
        thread1.start()

        # if self.editorModel.prop != key:
        #     toggle = item.checkState(column)
        #     self.editorModel.setVisibility(key, toggle)
        # else:
        #     item.setCheckState(0, Qt.Checked)
        # time.sleep(0.5)

    def on_tree_itemPressed(self, item, column):
        log = open('C:/Users/Public/Documents/log_file.txt', 'a')
        log.write('Выбор модели'+'\n')
        log.close()
        print('itemPressed')
        key = item.text(column)
        time.sleep(0.5)
        self.editorModel.prop = key

    def on_cbMeshColor_currentTextChanged(self, color_name):
        key = self.editorModel.prop
        if key:
            self.editorModel.props[key].color = get_color(color_name)
            self.editorModel.propsUpdated.emit()

    def on_pbSaveAll_pressed(self):
        log = open('C:/Users/Public/Documents/log_file.txt', 'a')
        log.write('Сохранить все модели'+'\n')
        log.close()
        file_name, _ = QFileDialog.getSaveFileName(self,
                                                   "Сохранить STL",
                                                   "",
                                                   "Файлы STL (*.stl)")
        if file_name:
            meshes = []
            for prop in self.editorModel.props:
                meshes.append(self.editorModel.props[prop].mesh)
            mesh = Mesh.from_meshes(meshes)

            mesh.save(file_name)
            print(file_name)

    def on_pbSave_pressed(self):
        log = open('C:/Users/Public/Documents/log_file.txt', 'a')
        log.write('Сохранить модель'+'\n')
        log.close()
        file_name, _ = QFileDialog.getSaveFileName(self,
                                                   "Сохранить STL",
                                                   "",
                                                   "Файлы STL (*.stl)")
        if file_name:
            self.editorModel.saveProp(file_name)
            print(file_name)

    def on_pbCopy_pressed(self):
        log = open('C:/Users/Public/Documents/log_file.txt', 'a')
        log.write('Создать копию модели'+'\n')
        log.close()
        self.editorModel.copyProp(self.editorModel.prop + '.cp')

    def on_pbDelete_pressed(self):
        log = open('C:/Users/Public/Documents/log_file.txt', 'a')
        log.write('Удалить модель'+'\n')
        log.close()
        self.editorModel.delProp()

def thread_tree_itemChanged(clc, key, toggle):
    time.sleep(0.2)
    if key in clc.editorModel._props:
        if clc.editorModel._props[key].is_visible != toggle:
            clc.editorModel._props[key].SetVisibility(toggle)
            clc.editorModel.propsUpdated.emit()
