"""Набор компонентов для взаимодействия с пользователем внутри сцены"""
import vtk
import numpy as np

from .image import Image
from .mesh import Mesh
from .color import get_color
from .cmap import cmap
from .display import PolyActor
from .geometry import vec_subtract, vec_normalize, vec_norm

class ImageView(object):

    def __init__(self, interactor, image, draw_contours=True, contour_threshold=400, upper_threshold=1500, window=400, level=200, colormap='grayscale'):
        self.interactor = interactor
        self._colormap = None
        self._lut = None
        self._image = None
        self._window = window
        self._level = level
        self.draw_contours = draw_contours
        self.contour_threshold = contour_threshold
        self.upper_threshold = upper_threshold
        self.on_cursor_changed = None
        self.on_windowlevel_changed = None

        self.contour_x = PolyActor(Mesh(), color='red', line_width=2.5)
        self.renderer.AddActor(self.contour_x)
        self.contour_y = PolyActor(Mesh(), color='green', line_width=2.5)
        self.renderer.AddActor(self.contour_y)
        self.contour_z = PolyActor(Mesh(), color='blue', line_width=2.5)
        self.renderer.AddActor(self.contour_z)


        self.plane_x = vtk.vtkImagePlaneWidget()
        self.plane_y = vtk.vtkImagePlaneWidget()
        self.plane_z = vtk.vtkImagePlaneWidget()


        picker = vtk.vtkCellPicker()
        picker.SetTolerance(0.005)
        for widget in [self.plane_x, self.plane_y, self.plane_z]:
            widget.SetPicker(picker)
            widget.DisplayTextOn()
            widget.SetRestrictPlaneToVolume(True)
            widget.SetResliceInterpolateToNearestNeighbour()
            widget.SetInteractor(self.interactor)
        self.image = image
        self.colormap = colormap
        self.window = window
        self.level = level
        self.update_contours()

        self.plane_x.AddObserver(vtk.vtkCommand.InteractionEvent, self.event)
        self.plane_x.AddObserver(vtk.vtkCommand.WindowLevelEvent, self.event)
        self.plane_y.AddObserver(vtk.vtkCommand.InteractionEvent, self.event)
        self.plane_y.AddObserver(vtk.vtkCommand.WindowLevelEvent, self.event)
        self.plane_z.AddObserver(vtk.vtkCommand.InteractionEvent, self.event)
        self.plane_z.AddObserver(vtk.vtkCommand.WindowLevelEvent, self.event)

        self.plane_x.SetRightButtonAction(vtk.vtkImagePlaneWidget.VTK_SLICE_MOTION_ACTION)
        self.plane_x.SetMiddleButtonAction(vtk.vtkImagePlaneWidget.VTK_WINDOW_LEVEL_ACTION)
        self.plane_y.SetRightButtonAction(vtk.vtkImagePlaneWidget.VTK_SLICE_MOTION_ACTION)
        self.plane_y.SetMiddleButtonAction(vtk.vtkImagePlaneWidget.VTK_WINDOW_LEVEL_ACTION)
        self.plane_z.SetRightButtonAction(vtk.vtkImagePlaneWidget.VTK_SLICE_MOTION_ACTION)
        self.plane_z.SetMiddleButtonAction(vtk.vtkImagePlaneWidget.VTK_WINDOW_LEVEL_ACTION)

    def event(self, caller, ev):
        if ev == 'InteractionEvent' and self.on_cursor_changed:
            self.on_cursor_changed(self.cursor)
            self.update_contours()

        if ev == 'WindowLevelEvent' and self.on_windowlevel_changed:
            self.window = caller.GetWindow()
            self.level = caller.GetLevel()
            self.on_windowlevel_changed(self.window, self.level)

    def update_contours(self):
        image = Image(self.plane_x.GetResliceOutput())
        contour = image.extract_contour(isovalue=self.contour_threshold)
        print('Contour threshold: ', self.contour_threshold)
        self.contour_x.mesh = contour
        self.contour_x.SetUserMatrix(self.plane_x.GetResliceAxes())
        #self.contour_x.SetPosition(self.plane_x.GetCenter())

        # for d in dir(self.plane_x):
        #     print(d)

        image = Image(self.plane_y.GetResliceOutput())
        contour = image.extract_contour(isovalue=self.contour_threshold)
        self.contour_y.mesh = contour
        self.contour_y.SetUserMatrix(self.plane_y.GetResliceAxes())


        image = Image(self.plane_z.GetResliceOutput())
        image.clip_values(minimum_value=image.min_value, maximum_value=self.upper_threshold, inplace=True)
        contour = image.extract_contour(isovalue=self.contour_threshold)
        self.contour_z.mesh = contour
        self.contour_z.SetUserMatrix(self.plane_z.GetResliceAxes())

    @property
    def renderer(self):
        return self.interactor.GetRenderWindow().GetRenderers().GetFirstRenderer()

    @property
    def cursor(self):
        return (self.plane_x.GetSliceIndex(),
                self.plane_y.GetSliceIndex(),
                self.plane_z.GetSliceIndex())

    @cursor.setter
    def cursor(self, value):
        x, y, z = value
        self.plane_x.SetSliceIndex(x)
        self.plane_y.SetSliceIndex(y)
        self.plane_z.SetSliceIndex(z)

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, value):
        self._image = value
        self.reset()

    @property
    def colormap(self):
        return self._colormap

    @colormap.setter
    def colormap(self, value):
        self._colormap = value
        self.lut = cmap(mapping=self.colormap,
                        min_value=self.image.min_value,
                        max_value=self.image.max_value)

    @property
    def lut(self):
        return self._lut

    @lut.setter
    def lut(self, value):
        self._lut = value
        self.plane_x.SetLookupTable(self.lut)
        self.plane_y.SetLookupTable(self.lut)
        self.plane_z.SetLookupTable(self.lut)

        self.plane_x.SetWindowLevel(self.window, self.level)
        self.plane_y.SetWindowLevel(self.window, self.level)
        self.plane_z.SetWindowLevel(self.window, self.level)

    @property
    def window(self):
        return self._window

    @window.setter
    def window(self, value):
        self._window = value
        self.plane_x.SetWindowLevel(self.window, self.level)
        self.plane_y.SetWindowLevel(self.window, self.level)
        self.plane_z.SetWindowLevel(self.window, self.level)

    @property
    def level(self):
        return self._level

    @level.setter
    def level(self, value):
        self._level = value
        self.plane_x.SetWindowLevel(self.window, self.level)
        self.plane_y.SetWindowLevel(self.window, self.level)
        self.plane_z.SetWindowLevel(self.window, self.level)

    def reset(self):
        self.plane_x.SetInputData(self.image)
        self.plane_x.SetPlaneOrientationToXAxes()
        self.plane_x.SetSliceIndex(int(self.image.width / 2))
        self.plane_x.GetPlaneProperty().SetColor(get_color('red'))

        self.plane_y.SetInputData(self.image)
        self.plane_y.SetPlaneOrientationToYAxes()
        self.plane_y.SetSliceIndex(int(self.image.height / 2))
        self.plane_y.GetPlaneProperty().SetColor(get_color('green'))

        self.plane_z.SetInputData(self.image)
        self.plane_z.SetPlaneOrientationToZAxes()
        self.plane_z.SetSliceIndex(int(self.image.depth / 2))
        self.plane_y.GetPlaneProperty().SetColor(get_color('blue'))

    def show(self):
        self.plane_x.On()
        self.plane_y.On()
        self.plane_z.On()

    def hide(self):
        self.plane_x.Off()
        self.plane_y.Off()
        self.plane_z.Off()

        self.renderer.RemoveActor(self.contour_x)
        self.renderer.RemoveActor(self.contour_y)
        self.renderer.RemoveActor(self.contour_z)


class Label(object):

    def __init__(self, interactor, text='', pos=(0, 0), fontsize=18, color='black'):
        self.interactor = interactor
        self._x = self._y = 0
        self._visible = True

        self.actor = vtk.vtkTextActor()
        self.renderer.AddActor(self.actor)
        self.x, self.y = pos
        self.text = text
        self.color = color
        self.fontsize = fontsize

    @property
    def renderer(self):
        return self.interactor.GetRenderWindow().GetRenderers().GetFirstRenderer()

    @property
    def size(self):
        sz = [0, 0]
        self.actor.GetSize(self.renderer, sz)
        return sz

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @x.setter
    def x(self, value):
        self._x = value
        self.actor.SetDisplayPosition(int(self.x), int(self.y))

    @y.setter
    def y(self, value):
        self._y = value
        self.actor.SetDisplayPosition(int(self.x), int(self.y))

    @property
    def pos(self):
        return self.x, self.y

    @pos.setter
    def pos(self, value):
        self.x, self.y = value

    @property
    def width(self):
        return self.size[0]

    @property
    def height(self):
        return self.size[1]

    @property
    def is_visible(self):
        return self._visible

    def show(self):
        if not self.is_visible:
            self._visible = True
            self.renderer.AddActor(self.actor)

    def hide(self):
        if self.is_visible:
            self._visible = False
            self.renderer.RemoveActor(self.actor)

    @property
    def color(self):
        return self.actor.GetTextProperty().GetColor()

    @color.setter
    def color(self, value):
        self.actor.GetTextProperty().SetColor(get_color(value))

    @property
    def fontsize(self):
        return self.actor.GetTextProperty().GetFontSize()

    @fontsize.setter
    def fontsize(self, value):
        self.actor.GetTextProperty().SetFontSize(value)

    @property
    def text(self):
        return self.actor.GetInput()

    @text.setter
    def text(self, value):
        self.actor.SetInput(value)


class Button(object):
    def __init__(self, interactor, states, size=(50, 50), pos=(0.0, 0.0), on_click=None):
        self.interactor = interactor
        self.on_click = on_click
        self._x, self._y = pos
        self._width, self._height = size

        self.rep = vtk.vtkTexturedButtonRepresentation2D()
        self.rep.SetNumberOfStates(len(states))
        for idx, state in enumerate(states):
            self.rep.SetButtonTexture(idx, state)

        self.widget = vtk.vtkButtonWidget()
        self.widget.SetInteractor(self.interactor)
        self.widget.SetRepresentation(self.rep)
        self.rep.SetPlaceFactor(1)
        self.rep.PlaceWidget(self.bounds)

        self.widget.AddObserver(vtk.vtkCommand.StateChangedEvent, self.callback)

    def set_on_click(self, callback):
        self.on_click = callback

    def callback(self, caller, event):
        if self.on_click:
            self.on_click()

    @property
    def renderer(self):
        return self.interactor.GetRenderWindow().GetRenderers().GetFirstRenderer()

    @property
    def size(self):
        return self.width, self.height

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @x.setter
    def x(self, value):
        self._x = value

    @y.setter
    def y(self, value):
        self._y = value

    @property
    def bounds(self):
        return [self.x,
                self.x + self.width,
                self.y,
                self.y + self.height, 0.0, 0.0]

    @property
    def pos(self):
        return self.x, self.y

    @pos.setter
    def pos(self, value):
        self.x, self.y = value

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    def show(self):
        self.widget.On()

    def hide(self):
        self.widget.Off()

    @property
    def state(self):
        return self.widget.GetRepresentation().GetState()

class TextButton(object):
    def __init__(self, interactor, label='hedddddddddddddllo', size=(50, 50), pos=(0.0, 0.0), on_click=None):
        self.interactor = interactor

        self.text_source = vtk.vtkVectorText()
        self.text_source.SetText(label)
        self.text_source.Update()
        self.text_mapper = vtk.vtkPolyDataMapper2D()
        self.text_mapper.SetInputConnection(self.text_source.GetOutputPort())
        self.text_actor = vtk.vtkActor2D()
        self.text_actor.SetMapper(self.text_mapper)
        self.text_actor.GetProperty().SetColor(1.0, 0.0, 0.0)

        bounds = self.text_actor.GetBounds()


        self.button_source = vtk.vtkRectangularButtonSource()
        self.button_source.Update()
        self.button_mapper = vtk.vtkPolyDataMapper()
        self.button_mapper.SetInputConnection(self.button_source.GetOutputPort())
        self.button_actor = vtk.vtkActor()
        self.button_actor.SetMapper(self.button_mapper)
        print(self.button_actor.GetBounds())

        self.renderer.AddActor2D(self.text_actor)
        self.renderer.AddActor(self.button_actor)

    @property
    def renderer(self):
        return self.interactor.GetRenderWindow().GetRenderers().GetFirstRenderer()





class DistanceMeasurer(object):
    def __init__(self, interactor, on_distance_changed=None):
        self.interactor = interactor
        self.on_distance_changed = on_distance_changed

        self.widget = vtk.vtkDistanceWidget()
        self.widget.SetInteractor(self.interactor)
        self.widget.CreateDefaultRepresentation()
        self.widget.GetDistanceRepresentation().SetLabelFormat("%-#6.3g mm")
        self.widget.AddObserver(vtk.vtkCommand.InteractionEvent, self.callback)

    @property
    def value(self):
        return self.widget.GetDistanceRepresentation().GetDistance()

    def set_on_distance_changed(self, callback):
        self.on_distance_changed = callback

    def callback(self, caller, event):
        if self.on_distance_changed:
            self.on_distance_changed(self.widget.GetDistanceRepresentation().GetDistance())

    @property
    def is_visible(self):
        return self.widget.GetEnabled()

    def show(self):
        self.widget.On()

    def hide(self):
        self.widget.Off()


class AngleMeasurer(object):

    def __init__(self, interactor, on_angle_changed=None):
        self.interactor = interactor
        self.on_angle_changed = on_angle_changed

        self.widget = vtk.vtkAngleWidget()
        self.widget.SetInteractor(self.interactor)
        self.widget.CreateDefaultRepresentation()

        self.widget.AddObserver(vtk.vtkCommand.InteractionEvent, self.callback)
        #self.widget.GetRepresentation().PlaceWidget(actor.GetBounds())

    @property
    def value(self):
        return self.widget.GetAngleRepresentation().GetAngle()

    def set_on_angle_changed(self, callback):
        self.on_distance_changed = callback

    def callback(self, caller, event):
        if self.on_angle_changed:
            self.on_angle_changed(self.value)

    @property
    def is_visible(self):
        return self.widget.GetEnabled()

    def show(self):
        self.widget.On()

    def hide(self):
        self.widget.Off()


class CubeSelector(object):
    """         """

    def __init__(self, interactor, mesh):
        self.interactor = interactor
        self.original = mesh
        self.current = None

        self.ghost = PolyActor(self.original, color='white', opacity=0.1)
        self.precut = PolyActor(self.original, color='red', opacity=1.0)

        self.renderer.AddActor(self.ghost)
        self.renderer.AddActor(self.precut)

        # self.mesh_actor = PolyActor(self.original, color='blue', line_width=2.0)
        self.widget = vtk.vtkBoxWidget()
        self.widget.SetInteractor(interactor)
        self.widget.SetProp3D(self.precut)
        self.widget.PlaceWidget(self.original.bounds)

        self.widget.GetFaceProperty().SetEdgeColor(get_color('blue'))
        self.widget.GetSelectedFaceProperty().SetEdgeColor(get_color('yellow'))

        self.widget.AddObserver(vtk.vtkCommand.InteractionEvent, self.event)
        self.label = Label(self.interactor, text='')
        self.event(caller=None, ev=None)

    def event(self, caller, ev):
        self.current = self.original.clip_by_mesh(self.as_polydata())
        self.precut.mesh = self.current

        trans = vtk.vtkTransform()
        self.widget.GetTransform(trans)
        sx, sy, sz = trans.GetScale()
        bounds = self.original.bounds

        width = (bounds[1] - bounds[0])*sx
        height = (bounds[3] - bounds[2])*sy
        depth = (bounds[5] - bounds[4])*sz
        self.label.text = '{}\n{}\n{}'.format(width, height, depth)

    def callback(self, caller, ev):
        print

    @property
    def renderer(self):
        return self.interactor.GetRenderWindow().GetRenderers().GetFirstRenderer()


    def show(self):
        self.widget.On()

    def hide(self):
        self.widget.Off()

    def as_polydata(self):
        poly_data = vtk.vtkPolyData()
        self.widget.GetPolyData(poly_data)
        return poly_data

    def as_planes(self):
        planes = vtk.vtkPlanes()
        self.widget.GetPlanes(planes)
        return planes

class CubeManipulator(object):

    def __init__(self, interactor, actor, rotation=True, translation=True, scaling=True):
        self.interactor = interactor
        self.actor = actor
        self._transform = vtk.vtkTransform()

        self.widget = vtk.vtkBoxWidget()
        self.widget.SetInteractor(self.interactor)
        self.widget.SetPlaceFactor(1)
        self.widget.SetRotationEnabled(rotation)
        self.widget.SetTranslationEnabled(translation)
        self.widget.SetScalingEnabled(scaling)
        self.widget.AddObserver(vtk.vtkCommand.InteractionEvent, self.event)

    @property
    def transform(self):
        self.widget.GetTransform(self._transform)
        return self._transform

    @property
    def mesh(self):
        return self.actor.mesh.apply_transform(self.transform)

    def event(self, caller, ev):
        self.actor.SetUserTransform(self.transform)

    def show(self):
        self.widget.PlaceWidget(self.actor.GetBounds())
        self.widget.On()

    def hide(self):
        self.widget.Off()


class PlaneSelector(object):
    """         """

    class ImplicitPlaneInteractionCallback(object):
        """     """

        def __init__(self, plane=None):
            """     """
            self._plane = plane

        def __call__(self, caller, ev):
            """     """
            if hasattr(caller, 'GetRepresentation'):
                rep = caller.GetRepresentation()
                if hasattr(rep, 'GetPlane') and self._plane:
                    rep.GetPlane(self._plane)

    def __init__(self, interactor, plane, bounds):
        """     """
        self._iren = interactor
        self._bounds = bounds
        self._plane = plane
        self._callback = PlaneSelector.ImplicitPlaneInteractionCallback(self._plane)

        self.rep = vtk.vtkImplicitPlaneRepresentation()
        self.rep.SetPlaceFactor(1.25)
        print(self._bounds)
        self.rep.PlaceWidget(self._bounds)
        self.rep.SetNormal(self._plane.GetNormal())
        self.rep.SetOrigin(self._plane.GetOrigin())
        self.rep.DrawOutlineOff()
        self.rep.DrawPlaneOn()

        self.widget = vtk.vtkImplicitPlaneWidget2()
        self.widget.SetInteractor(self._iren)
        self.widget.SetRepresentation(self.rep)
        self.widget.AddObserver(vtk.vtkCommand.InteractionEvent,
                                self._callback)

    def _pos(self, value):
        origin = self._plane.GetOrigin()
        self._plane.SetOrigin(value, origin[1], origin[2])
        self.rep.SetOrigin(self._plane.GetOrigin())

    def show(self):
        self.widget.On()

    def hide(self):
        self.widget.Off()

    @property
    def plane(self):
        return self._plane


class Slider(object):
    tube_width = 0.008
    slider_length = 0.008
    title_height = 0.02
    label_height = 0.02

    class SliderCallback(object):
        """     """

        def __init__(self, call):
            """     """
            self._call = call

        def __call__(self, caller, ev):
            """     """
            if hasattr(caller, 'GetRepresentation'):
                rep = caller.GetRepresentation()
                if hasattr(rep, 'GetValue') and self._call:
                    value = rep.GetValue()
                    self._call(value)

    def __init__(self,
                 interactor,
                 value=0.0,
                 minimum_value=0.0,
                 maximum_value=100.0,
                 caption_text='',
                 position='bottom',
                 on_value_changed_callback=None):
        """     """
        self._minimum = minimum_value
        self._maximum = maximum_value
        self._init_value = value
        self._on_value_changed = on_value_changed_callback

        self.rep = vtk.vtkSliderRepresentation2D()
        self.rep.SetMinimumValue(self._minimum)
        self.rep.SetMaximumValue(self._maximum)
        self.rep.SetValue(self._init_value)
        self.rep.SetTitleText(caption_text)

        self.rep.GetPoint1Coordinate().SetCoordinateSystemToNormalizedDisplay()
        self.rep.GetPoint1Coordinate().SetValue(.1, .1)
        self.rep.GetPoint2Coordinate().SetCoordinateSystemToNormalizedDisplay()
        self.rep.GetPoint2Coordinate().SetValue(.9, .1)

        self.rep.SetTubeWidth(self.tube_width)
        self.rep.SetSliderLength(self.slider_length)
        self.rep.SetTitleHeight(self.title_height)
        self.rep.SetLabelHeight(self.label_height)

        self.widget = vtk.vtkSliderWidget()
        self.widget.SetInteractor(interactor)
        self.widget.SetRepresentation(self.rep)
        self.widget.SetAnimationModeToAnimate()
        # self.widget.EnabledOn()

        self.widget.AddObserver('EndInteractionEvent',
                                Slider.SliderCallback(on_value_changed_callback))

    @property
    def value(self):
        return self.rep.GetValue()

    def show(self):
        self.widget.EnabledOn()

    def hide(self):
        self.widget.EnabledOff()

class LineProbe(object):

    def __init__(self, interactor, prop, on_changed=None):
        self.interactor = interactor
        self.on_changed = on_changed

        self.widget = vtk.vtkLineWidget()
        self.widget.SetInteractor(self.interactor)
        self.widget.SetProp3D(prop)
        self.widget.AddObserver(vtk.vtkCommand.EndInteractionEvent, self.callback)

    def place(self, bounds):
        self.widget.PlaceWidget(bounds)

    def place_at_point(self, pt):
        x, y, z = pt
        self.widget.SetPoint1(x-0.1, y-0.1, z)
        self.widget.SetPoint2(x+0.1, y+0.1, z)

    def as_polydata(self):
        tmp = Mesh()
        self.widget.GetPolyData(tmp)
        return tmp

    def set_on_angle_changed(self, callback):
        self.on_changed = callback

    def callback(self, caller, event):
        spline = vtk.vtkSplineFilter()
        spline.SetInputData(self.as_polydata())
        spline.SetSubdivideToSpecified()
        spline.SetNumberOfSubdivisions(256)
        spline.Update()

        sample_volume = vtk.vtkProbeFilter()
        sample_volume.SetInputData(1, self.image)
        sample_volume.SetInputData(0, spline.GetOutput())
        sample_volume.Update()
        samples = sample_volume.GetOutput().GetPointData().GetArray(0)
        samples = np.array([samples.GetValue(i) for i in range(samples.GetNumberOfValues())])
        if self.on_changed:
            self.on_changed(samples)

    def show(self):
        self.widget.On()

    def hide(self):
        self.widget.Off()

class SphereWidget(vtk.vtkSphereWidget):

    def __init__(self, interactor, center=(0, 0, 0), radius=15.0, callback=None):
        super().__init__()
        self.interactor = interactor
        self.callback = None

        self.picker = vtk.vtkWorldPointPicker()
        self.interactor.SetPicker(self.picker)
        self.SetInteractor(self.interactor)
        self.SetRepresentationToSurface()
        self.GetSphereProperty().SetColor(0, 1, 0)
        self.GetSelectedSphereProperty().SetColor(0, 1, 1)
        self.SetHandleVisibility(True)

        self.center = center
        self.radius = radius

        self.interactor.AddObserver(vtk.vtkCommand.MouseMoveEvent, self.on_mouse_move)
        self.interactor.AddObserver(vtk.vtkCommand.InteractionEvent, self.on_interaction_event)
        self.interactor.AddObserver(vtk.vtkCommand.EndInteractionEvent, self.on_end_interaction_event)

    def on_mouse_move(self, caller, event):
        # super().OnMouseMove()
        # dx, dy = self.interactor.GetEventPosition()
        # self.picker.Pick(dx, dy, 0, self.renderer)
        # x, y, z = self.picker.GetPickPosition()
        # self.center = (x, y, z)
        pass

    def on_interaction_event(self, caller, event):
        if self.callback:
            self.callback()

    def on_end_interaction_event(self, caller, event):
        pass

    @property
    def renderer(self):
        return self.interactor.GetRenderWindow().GetRenderers().GetFirstRenderer()

    @property
    def center(self):
        return self.GetCenter()

    @center.setter
    def center(self, value):
        self.SetCenter(value)

    @property
    def radius(self):
        return self.GetRadius()

    @radius.setter
    def radius(self, value):
        self.SetRadius(value)

    @property
    def direction(self):
        return self.GetHandleDirection()

    def as_mesh(self):
        polydata = vtk.vtkPolyData()
        self.GetPolyData(polydata)
        return Mesh(polydata)

    def as_sphere(self):
        sphere = vtk.vtkSphere()
        self.GetSphere(sphere)
        return sphere

    def show(self):
        self.On()

    def hide(self):
        self.Off()


class ArrowProbe(object):

    def __init__(self, interactor, origin, on_changed=None):
        self.interactor = interactor
        self.on_changed = on_changed

        self.widget = vtk.vtkLineWidget2()
        self.widget.SetInteractor(self.interactor)
        self.widget.CreateDefaultRepresentation()
        self.representation = self.widget.GetRepresentation()
        self.representation.DirectionalLineOn()
        self.representation.DistanceAnnotationVisibilityOn()
        self.representation.DragableOff()
        self.point1 = origin

        self.widget.AddObserver(vtk.vtkCommand.EndInteractionEvent, self.callback)

    @property
    def point1(self):
        return self.representation.GetPoint1WorldPosition()

    @point1.setter
    def point1(self, value):
        self.representation.SetPoint1WorldPosition(value)

    @property
    def point2(self):
        return self.representation.GetPoint2WorldPosition()

    @point2.setter
    def point2(self, value):
        self.representation.SetPoint2WorldPosition(value)

    @property
    def origin(self):
        return self.point1

    @property
    def direction(self):
        vec = vec_normalize(vec_subtract(self.point2, self.origin))
        return vec

    @property
    def length(self):
        vec = vec_subtract(self.point2, self.origin)
        return vec_norm(vec)

    def callback(self, caller, event):
        if self.on_changed:
            self.on_changed()

    def show(self):
        self.widget.On()

    def hide(self):
        self.widget.Off()