from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

from libcore.display import PolyActor
from libcore.mesh import Mesh, save_mesh_to_hdf, read_mesh_from_hdf
from libcore.color import random_mesh_color


class ImplantorModel(QObject):
    propSelected = pyqtSignal()
    propsUpdated = pyqtSignal()
    crossSectionUpdated = pyqtSignal(bool)
    ruler3DUpdated = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self._prop = None
        self._props = {}

        self.cutterPolyline = ToolCutterPolyline(self)
        self.cutterRect = ToolCutterRect(self)
        self.cutterCircle = ToolCutterCircle(self)
        self.cutterCube = ToolCutterCube(self)
        self.cutterSphere = ToolCutterSphere(self)
        self.cutterPlane = ToolCutterPlane(self)

        self.splitter = ToolSplitter(self)

    @property
    def prop(self):
        return self._prop

    @prop.setter
    def prop(self, value):
        prop = value if (self.prop != value) else None

        if self.prop in self._props:
            propUnselect(self._props[self.prop])
        if prop:
            if value in self._props:
                propSelect(self._props[value])
        else:
            self.cutterPolyline.toggle = False
            self.cutterRect.toggle = False
            self.cutterCircle.toggle = False
            self.cutterCube.toggle = False
            self.cutterSphere.toggle = False
            self.cutterPlane.toggle = False

        self._prop = prop
        self.propSelected.emit()

    @property
    def props(self):
        return self._props

    @pyqtSlot(str)
    def getVisibility(self, key):
        if key in self._props:
            return self._props[key].GetVisibility()

    @pyqtSlot(str, bool)
    def setVisibility(self, key, toggle):
        if self.prop != key:
            print('{} setVisibility!!! toggle={}'.format(__file__, toggle))
            if key in self._props:
                self._props[key].SetVisibility(toggle)
        self.propsUpdated.emit()

    @pyqtSlot(str)
    def getProp(self, key):
        if key in self._props:
            return self._props[key]
        return None

    @pyqtSlot(str, PolyActor)
    def addProp(self, key, prop):
        key = self._uname(key)
        prop.color = random_mesh_color()
        self._props[key] = prop
        if len(self.props) == 1:
            self.prop = key
        self.propsUpdated.emit()
        return key

    def reProp(self, key, mesh):
        if key in self._props:
            prop = PolyActor(mesh)
            prop.color = self._props[key].color
            prop.ambient = self._props[key].ambient
            prop.diffuse = self._props[key].diffuse
            prop.specular = self._props[key].specular
            prop.specular_power = self._props[key].specular_power
            self._props[key] = prop

        self.propsUpdated.emit()

    @pyqtSlot(str, list)
    def addProps(self, key, props):
        for prop in props:
            key_ = self._uname(key)
            self._props[key_] = prop
        self.propsUpdated.emit()

    @pyqtSlot(str)
    def copyProp(self, key):
        if self.prop:
            mesh = Mesh(self._props[self.prop].mesh)
            self.addProp(key, PolyActor(mesh))

    @pyqtSlot(str)
    def saveProp(self, file_path):
        if self.prop:
            self._props[self.prop].mesh.save(file_path)

    @pyqtSlot()
    def delProp(self):
        if self.prop:
            del self._props[self.prop]
            self.prop = None
            self.propsUpdated.emit()

    def save_to_hdf(self, fd):
        grp = fd.create_group('meshes')
        for name in self.props:
            grp[name] = '1'
            save_mesh_to_hdf(fd, name, self.props[name].mesh)

    def load_from_hdf(self, fd):
        if 'meshes' in fd:
            for key in fd['meshes']:
                prop = PolyActor(read_mesh_from_hdf(fd, key))
                self.addProp(key, prop)

    def _uname(self, name):
        names = self.props.keys()
        if name in names:
            for i in range(100000):
                index = name + '.' + str(i)
                if index not in names:
                    return index
        else:
            return name


def propSelect(prop):
    prop.ambient = 0.6
    prop.diffuse = 0.4
    prop.specular = 0.5
    prop.specular_power = 30.0


def propUnselect(prop):
    prop.ambient = 0.0
    prop.diffuse = 1.0
    prop.specular = 0.0
    prop.specular_power = 0.0


class ToolCutter(QObject):
    toolUpdated = pyqtSignal(QObject)

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.parent = parent
        self._name = None
        self._toggle = False
        self._inverse = False
        self._selection = None
        self._precut = None

        self.parent.propSelected.connect(self.updateSelect)

    def updateSelect(self):
        if self.parent.prop:
            if self.toggle:
                self.update()
        else:
            self.toggle = False

    def update(self, selection=None):
        if selection:
            self._selection = selection
        if self._selection and self.parent.prop:
            if self.parent.prop:
                _prop = self.parent.props[self.parent.prop]
                _prop.opacity = 0.1

                precut = _prop.mesh.clip_by_mesh(self._selection,
                                                 self.inverse,
                                                 inplace=False)
                self._precut = PolyActor(precut,
                                         color=_prop.color)
                propSelect(self.precut)
                self.toolUpdated.emit(self)

    def cut(self):
        if self._selection and self.parent.prop:
            if self._precut:
                self.parent.props[self.parent.prop] = self._precut

        self._selection = None
        self._precut = None
        self.toolUpdated.emit(self)
        self.parent.propsUpdated.emit()

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def toggle(self):
        return self._toggle

    @toggle.setter
    def toggle(self, value):
        if self._toggle == value:
            return

        self._toggle = value

        if not self.toggle:
            if self.parent.prop in self.parent.props:
                self.parent.props[self.parent.prop].opacity = 1.0
            self._precut = None
            self.parent.propsUpdated.emit()

        self.toolUpdated.emit(self)

    @property
    def inverse(self):
        return self._inverse

    @inverse.setter
    def inverse(self, value):
        if self._inverse == value:
            return

        if self.parent.prop:
            self._inverse = value
            self.toolUpdated.emit(self)
            self.update()

    @property
    def precut(self):
        return self._precut


class ToolCutterPolyline(ToolCutter):

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self._name = 'polyline'


class ToolCutterRect(ToolCutter):

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self._name = 'rect'


class ToolCutterCircle(ToolCutter):
    cutUpdated = pyqtSignal(QObject)

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self._name = 'circle'

    def cut(self):
        self.cutUpdated.emit(self)


class ToolCutterCube(ToolCutter):

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self._name = 'cube'


class ToolCutterSphere(ToolCutter):
    cutUpdated = pyqtSignal(QObject)

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self._name = 'sphere'

    def cut(self):
        self.cutUpdated.emit(self)


class ToolCutterPlane(ToolCutter):
    cutUpdated = pyqtSignal(QObject)

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self._name = 'plane'

    def cut(self):
        self.cutUpdated.emit(self)


class ToolSplitter(QObject):
    toolUpdated = pyqtSignal(QObject)

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.parent = parent
        self._name = 'splitter'
        self._toggle = False
        self._number = 20
        self._size = 0
        self._parts = []

        self.parent.propSelected.connect(self.updateSelect)

    def updateSelect(self):
        if self.parent.prop:
            if self.toggle:
                self.update()
        else:
            self.toggle = False

    def update(self, number=None, size=None):
        if number != None:
            self._number = number
        if size != None:
            self._size = size

        if self.parent.prop in self.parent.props:
            prop = self.parent.props[self.parent.prop]
            if self.size == 0:
                self._parts = [PolyActor(mesh, color=random_mesh_color())
                               for mesh in prop.mesh.split(n_largest=int(self._number))]
            elif self.size == 1:
                self._parts = [PolyActor(mesh, color=random_mesh_color())
                               for mesh in prop.mesh.split(n_smallest=int(self._number))]
            self.toolUpdated.emit(self)

    def cut(self):
        if self.parent.prop in self.parent.props:
            if len(self.parts) > 0:
                self.parent.addProps(self.parent.prop + '.splt', self.parts)
                self.parent.delProp()

        self._parts = []
        self.toolUpdated.emit(self)
        self.parent.propsUpdated.emit()

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def toggle(self):
        return self._toggle

    @toggle.setter
    def toggle(self, value):
        if self._toggle == value:
            return

        self._toggle = value

        if not self.toggle:
            if self.parent.prop in self.parent.props:
                self.parent.props[self.parent.prop].opacity = 1.0
            self._precut = None

        self.toolUpdated.emit(self)

    @property
    def number(self):
        return self._number

    @number.setter
    def number(self, value):
        self._number = value
        self.update()

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        self._size = value
        self.update()

    @property
    def parts(self):
        return self._parts


implantorModel = ImplantorModel()
