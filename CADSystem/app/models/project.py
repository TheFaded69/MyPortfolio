from PyQt5.QtCore import QObject


class ProjectModel(QObject):

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self._path = None

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        self._path = value

    def load(self, path):
        self.path = path

    def save(self, path):
        pass


projectModel = ProjectModel()
