from abc import ABC, abstractmethod
from contextlib import contextmanager
from functools import wraps

import vtk

from . import cmap


class ViewportMixin(object):
    OrientAnteriorPosterior = (0.0, 1.0, 0.0)  # Передний вид
    OrientPosteriorAnterior = (0.0, -1.0, 0.0)  # Задний вид
    OrientLeftAnteriorOblique = (1.0, 1.0, 0.0)  # Левый передний косой
    OrientRightAnteriorOblique = (-1.0, -1.0, 0.0)  # Правый передний косой
    OrientSuperiorInferior = (0.0, 0.0, 1.0)  # Сверху
    OrientInferiorSuperior = (0.0, 0.0, -1.0)  # Снизу
    OrientLeftLateral = (1.0, 0.0, 0.0)  # Левый боковой
    OrientRightLateral = (-1.0, 0.0, 0.0)  # Правый боковой

    def __init__(self):
        self._running = False

        try:
            print('The first occurance')
            self._interactor = self._Iren
        except:
            print('The second occurance')
            self._interactor = vtk.vtkRenderWindowInteractor()
            renderer = vtk.vtkRenderer()
            window = vtk.vtkRenderWindow()
            window.AddRenderer(renderer)
            self.interactor.SetRenderWindow(window)

        self.rwindow.SetSize(1024, 800)
        self.set_background_color('paraview')
        self.renderer.SetUseDepthPeeling(True)
        self.interactor.Initialize()
        self.rwindow.Render()

    @property
    def interactor(self):
        return self._interactor

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
    def style(self):
        return self.interactor.GetInteractorStyle()

    @property
    def size(self):
        return self.renderer.GetSize()

    @property
    def width(self):
        return self.size[0]

    @property
    def height(self):
        return self.size[1]

    @property
    def bounds(self):
        return self.renderer.ComputeVisiblePropBounds()

    @style.setter
    def style(self, value):
        if self.style == value:
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
        self.camera.SetViewUp(1, 0, 0)
        self.camera.OrthogonalizeViewUp()
        self.renderer.ResetCamera()

    def look_ap(self):
        self.look_from(ViewportMixin.OrientAnteriorPosterior)

    def look_pa(self):
        self.look_from(ViewportMixin.OrientPosteriorAnterior)

    def look_lao(self):
        self.look_from(ViewportMixin.OrientLeftAnteriorOblique)

    def look_rao(self):
        self.look_from(ViewportMixin.OrientRightAnteriorOblique)

    def look_sup(self):
        self.look_from(ViewportMixin.OrientSuperiorInferior)

    def look_inf(self):
        self.look_from(ViewportMixin.OrientInferiorSuperior)

    def look_ll(self):
        self.look_from(ViewportMixin.OrientLeftLateral)

    def look_rl(self):
        self.look_from(ViewportMixin.OrientRightLateral)

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

    def run(self):
        self._running = True
        self.rwindow.Render()
        self.renderer.ResetCamera()
        self.renderer.ResetCameraClippingRange()
        self.look_from(ViewportMixin.OrientAnteriorPosterior)
        self.zoom(1.5)
        self.interactor.Initialize()
        self.interactor.Start()


class InplaceMix(ABC):
    """ Абстракатный класс-примесь описывающий интерфейс переключаемого
        совершение над данными класса либо возвращение нового экземпляра класса"""

    def __init__(self):
        self.__inplace = False

    def inplace_off(self):
        self.__inplace = False

    def inplace_on(self):
        self.__inplace = True

    def is_inplace(self):
        return self.__inplace

    @abstractmethod
    def overwrite(self, data):
        raise NotImplementedError


class inplaceble(object):
    """ Дескриптор-декоратор для помечания"""

    def __init__(self, func):
        self.func = func

    def __get__(self, instance, owner):
        @wraps(self.func)
        def decorator(*args, **kwargs):
            if 'inplace' in kwargs:
                inplace = kwargs.pop('inplace')
            else:
                inplace = False
            result = self.func(instance, *args, **kwargs)
            if instance.is_inplace() or inplace:
                instance.overwrite(result)
            else:
                cls = type(instance)
                return cls(result)

        return decorator


@contextmanager
def inplace(obj):
    if not isinstance(obj, InplaceMix):
        msg = 'inplace должно использоваться только с производными от InplaceMix'
        raise TypeError(msg)
    obj.inplace_on()
    yield obj
    obj.inplace_off()
