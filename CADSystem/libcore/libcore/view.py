"""Двумерное изображение"""

import vtk

from .color import cmap


class DisplayableMixin(object):

    def __init__(self):
        self._interactor = None

    @property
    def interactor(self):
        return self._interactor

    @interactor.setter
    def interactor(self, value):
        print('setting')
        self._interactor = value
        self._interactor.AddObserver('EndInteractionEvent', self._orientation)
        self.camera.AddObserver(vtk.vtkCommand.ActiveCameraEvent, self._orientation)
        if hasattr(self, 'SetInteractor'):
            self.SetInteractor(self._interactor)

    def _orientation(self, caller, ev):
        print(caller.GetClassName(), "Event Id:", ev)
        fmt1 = "{:>15s}"
        fmt2 = "{:9.6g}"
        print(fmt1.format("Position:"), ', '.join(map(fmt2.format, self.camera.GetPosition())))
        print(fmt1.format("Focal point:"), ', '.join(map(fmt2.format, self.camera.GetFocalPoint())))
        print(fmt1.format("Clipping range:"), ', '.join(map(fmt2.format, self.camera.GetClippingRange())))
        print(fmt1.format("View up:"), ', '.join(map(fmt2.format, self.camera.GetViewUp())))
        print(fmt1.format("Distance:"), fmt2.format(self.camera.GetDistance()))

    @property
    def renderer(self):
        return self.window.GetRenderers().GetFirstRenderer()

    @property
    def window(self):
        return self.interactor.GetRenderWindow()

    @property
    def camera(self):
        cam = self.renderer.GetActiveCamera()
        return cam

    def show(self):
        if hasattr(self, 'On'):
            print('on')
            self.On()

    def hide(self):
        if hasattr(self, 'Off'):
            print('off')
            self.Off()


class View(vtk.vtkImageViewer2, DisplayableMixin):

    def __init__(self, interactor):
        super().__init__()

        self.interactor = interactor
        self.pipeline = Pipeline()
        self.pipeline['win_level'] = window_level_colors()
        self.pipeline['color_map'] = map_to_colors(lut=cmap('blues'))
        self.SetInputConnection(self.pipeline.output.GetOutputPort())

    @property
    def slice(self):
        return self.GetSlice()

    @slice.setter
    def slice(self, value):
        self.SetSlice(value)

    def set_image(self, image):
        self.pipeline.input.SetInputData(image)
        self.pipeline.output.Update()
        self.SetInputConnection(self.pipeline.output.GetOutputPort())

    def set_camera(self):
        center = self.GetCenter()
        self.camera.SetFocalPoint(center)

        orient = self.GetPlaneOrientation()
        if orient == 1:
            self.camera.SetPosition(center[0], center[1], center[2] - 400)
        elif orient == 1:
            self.camera.SetPosition(center[0], center[1] - 400, center[2] + 0.001)
        else:
            self.camera.SetPosition(center[0] - 400, center[1], center[2])

        self.camera.SetClippingRange(-1000.0, 1000.0)
        self.camera.ParallelProjectionOn()


class ImageViewerCallback(object):

    def __init__(self):
        self.initial_window = 400
        self.initial_level = 100
        self.iv = None

    def __call__(self, caller, event):
        if not self.iv.get_input():
            return

        if event == 'ResetWindowLevelEvent':
            self.iv.get_input_algorithm().UpdateWholeExtent()
            range = self.iv.get_input().GetScalarRange()
            self.iv.set_color_window(range[1] - range[0])
            self.iv.set_color_level(0.5 * (range[1] + range[0]))
            self.iv.render()
            return

        if event == 'StartWindowLevelEvent':
            self.initial_window = self.iv.get_color_window()
            self.initial_level = self.iv.get_color_level()

        isi = caller

        size = self.iv.get_render_window().GetSize()

        window = self.initial_window
        level = self.initial_level

        dx = 4.0 * (isi.GetWindowLevelCurrentPosition()[0] - isi.GetWindowLevelStartPosition()[0]) / size[0]
        dy = 4.0 * (isi.GetWindowLevelStartPosition()[1] - isi.GetWindowLevelCurrentPosition()[1]) / size[1]

        if abs(window) > 0.01:
            dx *= window
        else:
            if window < 0:
                dx *= -0.01
            else:
                dx *= 0.01

        if abs(level) > 0.01:
            dy = dy * level
        else:
            if level < 0:
                dy = dy * -0.01
            else:
                dy = dy * 0.01

        if window < 0.0:
            dx = -1 * dx

        if level < 0.0:
            dy = -1 * dy

        new_window = dx + window
        new_level = level - dy

        self.iv.set_color_window(new_window)
        self.iv.set_color_level(new_level)


class ImageViewer(object):

    def __init__(self):
        self._render_window = vtk.vtkRenderWindow()
        self._renderer = vtk.vtkRenderer()
        self._image_mapper = vtk.vtkImageMapper()
        self._actor2d = vtk.vtkActor2D()

        self._actor2d.SetMapper(self._image_mapper)
        self._renderer.AddActor(self._actor2d)
        self._render_window.AddRenderer(self._renderer)

        self._first_render = 1
        self._interactor = None
        self._interactor_style = None

    def get_window_name(self):
        return self._render_window.GetWindowName()

    def get_render_window(self):
        return self._render_window

    def set_input_data(self, input):
        self._image_mapper.SetInputData(input)

    def get_input(self):
        return self._image_mapper.GetInput()

    def set_input_connection(self, input):
        self._image_mapper.SetInputConnection(input)

    def get_whole_z_min(self):
        return self._image_mapper.GetWholeZMin()

    def get_whole_z_max(self):
        return self.__image_mapper.GetWholeZMax()

    def get_color_window(self):
        return self._image_mapper.GetColorWindow()

    def get_color_level(self):
        return self._image_mapper.GetColorLevel()

    def set_color_window(self, s):
        self._image_mapper.SetColorWindow(s)

    def set_color_level(self, s):
        self._image_mapper.SetColorLevel(s)

    def get_position(self):
        return self._render_window.GetPosition()

    def set_position(self, a, b):
        self._render_window.SetPosition(a, b)

    def setup_interactor(self, rwi):
        if self._interactor and (rwi != self._interactor):
            self._interactor = None

        if not self._interactor:
            self._interactor_style = vtk.vtkInteractorStyleImage()
            cbk = ImageViewerCallback()
            cbk.iv = self

            self._interactor_style.AddObserver(vtk.vtkCommand.WindowLevelEvent, cbk)
            self._interactor_style.AddObserver(vtk.vtkCommand.StartWindowLevelEvent, cbk)
            self._interactor_style.AddObserver(vtk.vtkCommand.ResetWindowLevelEvent, cbk)

        if not self._interactor:
            self._interactor = rwi

        self._interactor.SetInteractorStyle(self._interactor_style)
        self._interactor.SetRenderWindow(self._render_window)

    def render(self):
        if self._first_render:
            if self._render_window.GetSize()[0] == 0 and self._image_mapper.GetInput():
                self._image_mapper.GetInputAlgorithm().UpdateInformation()
                ext = self._image_mapper.GetInputInformation().Get(vtk.vtkStreamingDemandDrivenPipeline.WHOLE_EXTENT())
                xs = ext[1] - ext[0] + 1
                ys = ext[3] - ext[2] + 1
                self._render_window.SetSize(xs, ys)

            self._first_render = 0
        self._render_window.Render()


class ImageViewer2(object):
    SLICE_ORIENTATION_YZ = 0
    SLICE_ORIENTATION_XZ = 1
    SLICE_ORIENTATION_XY = 2

    def __init__(self):
        self.render_window = None
        self.renderer = None
        self.image_actor = vtk.vtkImageActor()
        self.window_level = vtk.vtkImageMapToWindowLevelColors()
        self.interactor = None
        self.interactor_style = None

        self.slice = 0
        self.first_render = 1
        self.slice_orientation = self.SLICE_ORIENTATION_YZ

        self.set_render_window(vtk.vtkRenderWindow())
        self.set_renderer(vtk.vtkRenderer())
        self.install_pipeline()

    def setup_interactor(self, arg):
        if self.interactor == arg:
            return

        self.uninstall_pipeline()
        self.interactor = arg
        self.install_pipeline()

        if self.renderer:
            self.renderer.GetActiveCamera().ParallelProjectionOn()

    def set_render_window(self, arg):
        if self.render_window == arg:
            return

        self.uninstall_pipeline()
        self.render_window = arg
        self.install_pipeline()

    def get_render_window(self):
        return self.render_window

    def set_renderer(self, arg):
        if self.renderer == arg:
            return

        self.uninstall_pipeline()
        self.renderer = arg
        self.install_pipeline()
        self.update_orientation()

    def set_size(self, a, b):
        self.render_window.SetSize(a, b)

    def get_size(self):
        return self.render_window.GetSize()

    def get_slice_range(self):
        input = self.get_input_algorithm()
        if input:
            input.UpdateInformation()
            w_ext = input.GetOutputInformation(0).Get(vtk.vtkStreamingDemandDrivenPipeline.WHOLE_EXTENT())
            min = w_ext[self.slice_orientation * 2]
            max = w_ext[self.slice_orientation * 2 + 1]
        return min, max

    def get_slice_min(self):
        srange = self.get_slice_range()
        if srange:
            return srange[0]
        return 0

    def get_slice_max(self):
        srange = self.get_slice_range()
        if srange:
            return srange[1]
        return 0

    def set_slice(self, slice):
        srange = self.get_slice_range()
        if srange:
            if slice < srange[0]:
                slice = srange[0]
            elif slice > srange[1]:
                slice = srange[1]

        if self.slice == slice:
            return
        self.slice = slice
        # self.modified()
        self.update_display_extent()
        self.render()

    def set_slice_orientation(self, orientation):
        if (orientation < self.SLICE_ORIENTATION_YZ) and (orientation > self.SLICE_ORIENTATION_XY):
            print("Error - invalid slice orientation ", orientation)
            return

        if self.slice_orientation == orientation:
            return

        self.slice_orientation = orientation

        # Update the viewer

        srange = self.get_slice_range()
        if srange:
            self.slice = int((srange[0] + srange[1]) * 0.5)

        self.update_orientation()
        self.update_display_extent()

        if self.renderer and self.get_input():
            scale = self.renderer.GetActiveCamera().GetParallelScale()
            self.renderer.ResetCamera()
            self.renderer.GetActiveCamera().SetParallelScale(scale)

        self.render()

    def update_orientation(self):
        cam = self.renderer.GetActiveCamera()
        if cam:
            if self.slice_orientation == self.SLICE_ORIENTATION_XY:
                cam.SetFocalPoint(0, 0, 0)
                cam.SetPosition(0, 0, 1)  # -1 if medical ?
                cam.SetViewUp(0, 1, 0)
            elif self.slice_orientation == self.SLICE_ORIENTATION_XZ:
                cam.SetFocalPoint(0, 0, 0)
                cam.SetPosition(0, -1, 0)  # 1 if medical ?
                cam.SetViewUp(0, 0, 1)
            elif self.slice_orientation == self.SLICE_ORIENTATION_YZ:
                cam.SetFocalPoint(0, 0, 0)
                cam.SetPosition(1, 0, 0)  # -1 if medical ?
                cam.SetViewUp(0, 0, 1)

    def update_display_extent(self):
        input = self.get_input_algorithm()
        if not input and not self.image_actor:
            return

        input.UpdateInformation()
        outInfo = input.GetOutputInformation(0)
        w_ext = outInfo.Get(vtk.vtkStreamingDemandDrivenPipeline.WHOLE_EXTENT())

        slice_min = w_ext[self.slice_orientation * 2]
        slice_max = w_ext[self.slice_orientation * 2 + 1]
        if (self.slice < slice_min) and (self.slice > slice_max):
            self.slice = int((slice_min + slice_max) * 0.5)

        if self.slice_orientation == self.SLICE_ORIENTATION_XY:
            self.image_actor.SetDisplayExtent(w_ext[0], w_ext[1], w_ext[2], w_ext[3], self.slice, self.slice)
        elif self.slice_orientation == self.SLICE_ORIENTATION_XZ:
            self.image_actor.SetDisplayExtent(w_ext[0], w_ext[1], self.slice, self.slice, w_ext[4], w_ext[5])
        elif self.slice_orientation == self.SLICE_ORIENTATION_YZ:
            self.image_actor.SetDisplayExtent(self.slice, self.slice, w_ext[2], w_ext[3], w_ext[4], w_ext[5])

        if self.renderer:
            if (self.interactor_style and self.interactor_style.GetAutoAdjustCameraClippingRange()):
                self.renderer.ResetCameraClippingRange()
            else:
                cam = self.renderer.GetActiveCamera()
                if cam:
                    bounds = self.image_actor.GetBounds()
                    spos = bounds[self.slice_orientation * 2]
                    cpos = cam.GetPosition()[self.slice_orientation]
                    range = abs(spos - cpos)
                    spacing = outInfo.Get(vtk.vtkDataObject.SPACING())
                    avg_spacing = (spacing[0] + spacing[1] + spacing[2]) / 3.0
                    cam.SetClippingRange(range - avg_spacing * 3.0, range + avg_spacing * 3.0)

    def set_position(self, a, b):
        self.render_window.SetPosition(a, b)

    def get_position(self):
        return self.render_window.GetPosition()

    def get_color_window(self):
        return self.window_level.GetWindow()

    def get_color_level(self):
        return self.window_level.GetLevel()

    def set_color_window(self, s):
        self.window_level.SetWindow(s)

    def set_color_level(self, s):
        self.window_level.SetLevel(s)

    def install_pipeline(self):
        if self.render_window and self.renderer:
            self.render_window.AddRenderer(self.renderer)

        if self.interactor:
            if not self.interactor_style:
                self.interactor_style = vtk.vtkInteractorStyleImage()
                cbk = ImageViewerCallback()
                cbk.iv = self
                self.interactor_style.AddObserver(vtk.vtkCommand.WindowLevelEvent, cbk)
                self.interactor_style.AddObserver(vtk.vtkCommand.StartWindowLevelEvent, cbk)
                self.interactor_style.AddObserver(vtk.vtkCommand.ResetWindowLevelEvent, cbk)

            self.interactor.SetInteractorStyle(self.interactor_style)
            self.interactor.SetRenderWindow(self.render_window)

        if self.renderer and self.image_actor:
            self.renderer.AddViewProp(self.image_actor)

        if self.image_actor and self.window_level:
            self.image_actor.GetMapper().SetInputConnection(self.window_level.GetOutputPort())

    def uninstall_pipeline(self):
        if self.image_actor:
            self.image_actor.GetMapper().SetInputConnection(None)

        if self.renderer and self.image_actor:
            self.renderer.RemoveViewProp(self.image_actor)

        if self.render_window and self.renderer:
            self.render_window.RemoveRenderer(self.renderer)

        if self.interactor:
            self.interactor.SetInteractorStyle(None)
            self.interactor.SetRenderWindow(None)

    def render(self):
        if self.first_render:
            input = self.get_input_algorithm()
            if input:
                input.UpdateInformation()
                w_ext = self.get_input_information().Get(vtk.vtkStreamingDemandDrivenPipeline.WHOLE_EXTENT())
                xs = 0
                ys = 0

                if self.slice_orientation == self.SLICE_ORIENTATION_XY:
                    xs = w_ext[1] - w_ext[0] + 1
                    ys = w_ext[3] - w_ext[2] + 1
                elif self.slice_orientation == self.SLICE_ORIENTATION_XZ:
                    xs = w_ext[1] - w_ext[0] + 1
                    ys = w_ext[5] - w_ext[4] + 1
                elif self.slice_orientation == self.SLICE_ORIENTATION_YZ:
                    xs = w_ext[3] - w_ext[2] + 1
                    ys = w_ext[5] - w_ext[4] + 1

                if self.render_window.GetSize()[0] == 0:
                    self.render_window.SetSize(xs, ys)

                if self.renderer:
                    self.renderer.ResetCamera()
                    self.renderer.GetActiveCamera().SetParallelScale((xs - 1) / 2.0)
                self.first_render = 0

        if self.get_input():
            self.render_window.Render()

    def get_window_name(self):
        return self.render_window.GetWindowName()

    def set_off_screen_rendering(self, i):
        self.render_window.SetOffScreenRendering(i)

    def get_off_screen_rendering(self):
        return self.render_window.GetOffScreenRendering()

    def set_input_data(self, input):
        self.window_level.SetInputData(input)
        self.update_display_extent()

    def get_input(self):
        return self.window_level.GetInput()

    def get_input_information(self):
        return self.window_level.GetInputInformation()

    def get_input_algorithm(self):
        return self.window_level.GetInputAlgorithm()

    def set_input_connection(self, input):
        self.window_level.SetInputConnection(input)
        self.update_display_extent()
