from PyQt5.QtCore import QObject, pyqtSignal

from libcore.mesh import Mesh


class MounterModel(QObject):
    loaded = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self._mesh = None
        self._implant = None
        self._full_mesh = None

    @property
    def mesh(self):
        return self._mesh

    @mesh.setter
    def mesh(self, value):
        self._mesh = value
        self.loaded.emit()

    @property
    def implant(self):
        return self._implant

    @implant.setter
    def implant(self, value):
        self._implant = value
        self.loaded.emit()

    @property
    def full_mesh(self):
        if self.mesh and self.implant:
            if self._full_mesh is None:
                self._full_mesh = Mesh.from_meshes([self.mesh,
                                                    self.implant])
                self._full_mesh.compute_normals()
        else:
            self._full_mesh = Mesh()

        return self._full_mesh


mounterModel = MounterModel()
