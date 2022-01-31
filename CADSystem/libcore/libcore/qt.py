import vtk
import vtk.qt
vtk.qt.QVTKRWIBase = "QGLWidget"
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget

from libcore import cmap



class MyQVTKRenderWindowInteractor(QVTKRenderWindowInteractor, QWidget):

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.modePan = False
        self.modeZoom = False
        self.modeRotate = False

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.modePan == True:
                self.GetInteractorStyle().StartPan()
            elif self.modeZoom == True:
                self.GetInteractorStyle().StartDolly()
            elif self.modeRotate == True:
                self.GetInteractorStyle().StartSpin()

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.GetInteractorStyle().EndPan()
            self.GetInteractorStyle().EndDolly()
            self.GetInteractorStyle().EndSpin()

        super().mouseReleaseEvent(event)

    def setModePan(self, toggle):
        self.modePan = toggle

    def setModeZoom(self, toggle):
        self.modeZoom = toggle

    def setModeRotate(self, toggle):
        self.modeRotate = toggle


class Viewport(MyQVTKRenderWindowInteractor):
    OrientAnteriorPosterior = (0.0, -1.0, 0.0)  # Передний вид
    OrientPosteriorAnterior = (0.0, 1.0, 0.0)  # Задний вид
    OrientLeftAnteriorOblique = (-1.0, -1.0, 0.0)  # Левый передний косой
    OrientRightAnteriorOblique = (1.0, -1.0, 0.0)  # Правый передний косой
    OrientSuperiorInferior = (0.00000001, 0.00000001, 1.0)  # Сверху
    OrientInferiorSuperior = (0.00000001, 0.00000001, -1.0)  # Снизу
    OrientLeftLateral = (-1.0, 0.0, 0.0)  # Левый боковой
    OrientRightLateral = (1.0, 0.0, 0.0)  # Правый боковой

    def __init__(self, parent=None):
        super().__init__(parent)
        self._running = False

        renderer = vtk.vtkRenderer()
        self.rwindow.AddRenderer(renderer)
        self.set_background_color('paraview')
        self.renderer.SetUseDepthPeeling(True)

    @property
    def interactor(self):
        return self._Iren

    @property
    def renderer(self):
        return self.interactor.GetRenderWindow().GetRenderers().GetFirstRenderer()

    @property
    def rwindow(self):
        return self.interactor.GetRenderWindow()

    @property
    def camera(self):
        return self.renderer.GetActiveCamera()

    @property
    def istyle(self):
        return self.interactor.GetInteractorStyle()

    @property
    def rsize(self):
        return self.renderer.GetSize()

    @property
    def rwidth(self):
        return self.rsize[0]

    @property
    def rheight(self):
        return self.rsize[1]

    @property
    def bounds(self):
        return self.ComputeVisiblePropBounds()

    @istyle.setter
    def istyle(self, value):
        if self.istyle == value:
            return
        self.interactor.SetInteractorStyle(value)

    def set_cursor(self, cursor_name='default'):
        cursors = {'arrow': vtk.VTK_CURSOR_ARROW,
                   'crosshair': vtk.VTK_CURSOR_CROSSHAIR,
                   'default': vtk.VTK_CURSOR_DEFAULT,
                   'hand': vtk.VTK_CURSOR_HAND,
                   'all': vtk.VTK_CURSOR_SIZEALL,
                   'ne': vtk.VTK_CURSOR_SIZENE,
                   'ns': vtk.VTK_CURSOR_SIZENS,
                   'nw': vtk.VTK_CURSOR_SIZENW,
                   'se': vtk.VTK_CURSOR_SIZESE,
                   'sw': vtk.VTK_CURSOR_SIZESW,
                   'we': vtk.VTK_CURSOR_SIZEWE}

        self.rwindow.SetCurrentCursor(cursors[cursor_name])

    def set_background_color(self, color):
        self.renderer.SetBackground(cmap.color(color))

    def look_from(self, point):
        self.camera.SetFocalPoint(0, 0, 0)
        self.camera.SetPosition(point)
        self.camera.ComputeViewPlaneNormal()
        self.camera.SetViewUp(0, 0, 1)
        self.camera.OrthogonalizeViewUp()
        self.renderer.ResetCamera()
        self.rwindow.Render()

    def look_ap(self):
        self.look_from(Viewport.OrientAnteriorPosterior)

    def look_pa(self):
        self.look_from(Viewport.OrientPosteriorAnterior)

    def look_lao(self):
        self.look_from(Viewport.OrientLeftAnteriorOblique)

    def look_rao(self):
        self.look_from(Viewport.OrientRightAnteriorOblique)

    def look_sup(self):
        self.look_from(Viewport.OrientSuperiorInferior)

    def look_inf(self):
        self.look_from(Viewport.OrientInferiorSuperior)

    def look_ll(self):
        self.look_from(Viewport.OrientLeftLateral)

    def look_rl(self):
        self.look_from(Viewport.OrientRightLateral)

    def add_prop(self, prop):
        self.renderer.AddActor(prop)
        if self._running:
            self.rwindow.Render()

    def add_props(self, props):
        for prop in props:
            self.renderer.AddActor(prop)
        if self._running:
            self.rwindow.Render()

    def remove_prop(self, prop):
        self.renderer.RemoveActor(prop)

    def actors(self):
        for actor in self.renderer.GetActors():
            yield actor

    def zoom(self, value):
        self.camera.Zoom(value)

    def dolly(self, value):
        self.camera.Dolly(value)

    def register_callback(self, event, callback):
        self.interactor.AddObserver(event, callback)

    def reset_view(self):
        self._running = True
        self.rwindow.Render()
        self.renderer.ResetCamera()
        self.renderer.ResetCameraClippingRange()
        self.look_from(Viewport.OrientAnteriorPosterior)
        self.zoom(1.2)
