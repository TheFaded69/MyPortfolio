import vtk

import numpy as np

from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import QWidget

from libcore.qt import Viewport
from libcore.color import cmap, get_color
from libcore.display import PolyActor
from libcore.geometry import Plane
from libcore.mesh import Mesh
from libcore import widget


from ..models.image import imageModel
from ..models.plane import PlaneModel, axialModel, coronalModel, sagittalModel
from ..models.editor import editorModel
from ..models.implantor import implantorModel
from ..models.histogram import histogramModel

from ..views.view2d_ui import Ui_View2D


class View2D(QWidget, Ui_View2D):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)

        self.setDisabled(True)
        self.on_tbTools_toggled(False)

        self.viewport = Viewport()
        self.viewport.istyle = vtk.vtkInteractorStyleImage()
        self.viewport.interactor.Initialize()
        self.layout.addWidget(self.viewport)

        self._viewer = vtk.vtkImagePlaneWidget()
        self._viewer.SetInteractor(self.viewport.interactor)
        self._viewer.GetTextProperty().SetColor(get_color('red'))
        self._viewer.DisplayTextOn()

        self.cmap_name = None

        self.imageModel = imageModel
        self.imageModel.imageLoaded.connect(self.loadImage)
        self.imageModel.imageUpdated.connect(self.updateImage)

        self.editorModel = editorModel
        self.implantorModel = implantorModel

        self.histogramModel = histogramModel

        self.loadImage()

    def loadImage(self):
        if hasattr(self, 'imageModel'):
            if self.imageModel.image:
                self.setEnabled(True)

                self._viewer.SetInputData(self.imageModel.image)
                self._viewer.SetPlaneOrientation(self.orientation)
                self._viewer.SetRestrictPlaneToVolume(True)
                self._viewer.SetResliceInterpolateToNearestNeighbour()
                self._viewer.On()

                self.updateSlice()
                self.updateCmap()

                camera = self.viewport.camera
                image_size = self.imageModel.image.GetDimensions()
                center = self.imageModel.image.GetCenter()
                camera.SetFocalPoint(center[0], center[1], center[2] + 0.001)

                if self.orientation == PlaneModel.SAGITTAL:
                    camera.SetPosition(center[0] + 400,
                                       center[1],
                                       center[2])
                    camera.SetRoll(270)
                elif self.orientation == PlaneModel.CORONAL:
                    camera.SetPosition(center[0],
                                       center[1] - 400,
                                       center[2])
                    camera.SetRoll(0)
                elif self.orientation == PlaneModel.AXIAL:
                    camera.SetPosition(center[0],
                                       center[1],
                                       center[2] - 400)
                    camera.SetRoll(180)

                camera.ComputeViewPlaneNormal()
                camera.ParallelProjectionOn()
                camera.SetParallelScale(image_size[0] / 5)

                self.viewport.renderer.ResetCamera()

                self.viewport.rwindow.Render()
                print("{} image loaded".format(self.objectName()))

    def updateImage(self):
        self.viewport.rwindow.Render()

    @pyqtSlot(int)
    def setOrientation(self, orientation):
        self.orientation = PlaneModel.AXIAL
        self.planeModel = axialModel

        if orientation == "sagittal":
            self.orientation = PlaneModel.SAGITTAL
            self.planeModel = sagittalModel
        elif orientation == "coronal":
            self.orientation = PlaneModel.CORONAL
            self.planeModel = coronalModel

        self.planeModel.sliceUpdated.connect(self.updateSlice)
        self.planeModel.cmapUpdated.connect(self.updateCmap)
        self.loadImage()

    @pyqtSlot(str)
    def setObjectName(self, name):
        super().setObjectName(name)
        self.setOrientation(name)

    @pyqtSlot()
    def updateSlice(self):
        slice_index = self.planeModel.slice

        if self.sSlice.maximum() != self.planeModel.slice_max:
            self.sSlice.setMaximum(self.planeModel.slice_max)
        if self.sSlice.value() != slice_index:
            self.sSlice.setValue(slice_index)
        if self.sbSlice.maximum() != self.planeModel.slice_max:
            self.sbSlice.setMaximum(self.planeModel.slice_max)
        if self.sbSlice.value() != slice_index:
            self.sbSlice.setValue(slice_index)

        if self._viewer.GetSliceIndex() == slice_index:
            return


        # for prop in self.editorModel.props:
        #     actor = self.editorModel.props[prop]
        #     plane = Plane.XY(origin=self._viewer.GetOrigin())
        #     clipped = actor.mesh.slice_by_plane(plane=plane)

        #     if hasattr(self, 'contour'):
        #         self.contour.mesh = clipped
        #     else:
        #         self.contour = PolyActor(mesh=clipped,
        #                                  color='red',
        #                                  render_lines_as_tubes=True,
        #                                  line_width=3)
        #         self.viewport.add_prop(self.contour)


        # for prop in self.implantorModel.props:
        #     actor = self.implantorModel.props[prop]
        #     plane = Plane.XY(origin=self._viewer.GetOrigin())
        #     clipped = actor.mesh.slice_by_plane(plane=plane)

        #     if hasattr(self, 'contour'):
        #         self.contour.mesh = clipped
        #     else:
        #         self.contour = PolyActor(mesh=clipped,
        #                                  color='green',
        #                                  render_lines_as_tubes=True,
        #                                  line_width=3)
        #         self.viewport.add_prop(self.contour)


        self._viewer.SetSliceIndex(slice_index)
        self.viewport.rwindow.Render()
        print("{} set slice: {}".format(self.objectName(),
                                        slice_index))

        if hasattr(self, 'line_widget'):
            self.line_widget.updateSlice(self._viewer.GetPlaneOrientation(),
                                         self._viewer.GetSlicePosition())

    @pyqtSlot()
    def updateCmap(self):
        if self.cmap_name != self.planeModel.cmap:
            self.cmap_name = self.planeModel.cmap
            self._viewer.SetLookupTable(cmap(mapping=self.cmap_name))
            print("{} set colormap: {}".format(
                self.objectName(), self.cmap_name))

        level = self.planeModel.level
        window = self.planeModel.window
        if self._viewer.GetLevel() != level or self._viewer.GetWindow() != window:
            self._viewer.SetWindowLevel(window, level)
            print("{} set window: {}".format(self.objectName(), window))
            print("{} set level: {}".format(self.objectName(), level))

    @pyqtSlot(bool)
    def on_tbTools_toggled(self, toggle):
        if toggle is True:
            self.tbTools.setArrowType(Qt.UpArrow)
        else:
            self.tbTools.setArrowType(Qt.DownArrow)

        self.tools.setVisible(toggle)

    @pyqtSlot(int)
    def on_sSlice_valueChanged(self, value):
        self.planeModel.slice = value

    @pyqtSlot(int)
    def on_sbSlice_valueChanged(self, value):
        self.planeModel.slice = value

    @pyqtSlot(bool)
    def on_toolButtonPan_toggled(self, toggle):
        log = open('C:/Users/Public/Documents/log_file.txt', 'a')
        log.write('Включить\выключить перемещение' + '\n')
        log.close()
        if toggle == True:
            self.viewport.setModePan(True)
            self._viewer.InteractionOff()
        else:
            self.viewport.setModePan(False)
            self._viewer.InteractionOn()

    @pyqtSlot(bool)
    def on_toolButtonZoom_toggled(self, toggle):
        log = open('C:/Users/Public/Documents/log_file.txt', 'a')
        log.write('Включить\выключить масштабирование' + '\n')
        log.close()
        if toggle == True:
            self.viewport.setModeZoom(True)
            self._viewer.InteractionOff()
        else:
            self.viewport.setModeZoom(False)
            self._viewer.InteractionOn()

    @pyqtSlot(bool)
    def on_toolButtonRotate_toggled(self, toggle):
        log = open('C:/Users/Public/Documents/log_file.txt', 'a')
        log.write('Включить\выключить поворот'+'\n')
        log.close()
        if toggle == True:
            self.viewport.setModeRotate(True)
            self._viewer.InteractionOff()
        else:
            self.viewport.setModeRotate(False)
            self._viewer.InteractionOn()

    @pyqtSlot(bool)
    def on_tbDistanceMeasurer_toggled(self, toggle):
        log = open('C:/Users/Public/Documents/log_file.txt', 'a')
        log.write('Включить\выключить измеритель длины' + '\n')
        log.close()
        if toggle == True:
            self.distance_widget = widget.DistanceMeasurer(self.viewport)
            self.distance_widget.show()
            # Выключаем обычное взаимодействие для виджета
            self._viewer.InteractionOff()
        else:
            if self.distance_widget:
                self.distance_widget.hide()
                self._viewer.InteractionOn()

    @pyqtSlot(bool)
    def on_tbAngleMeasurer_toggled(self, toggle):
        log = open('C:/Users/Public/Documents/log_file.txt', 'a')
        log.write('Включить\выключить измеритель угла' + '\n')
        log.close()
        if toggle == True:
            self.angle_widget = widget.AngleMeasurer(self.viewport)
            self.angle_widget.show()
            # Выключаем обычное взаимодействие для виджета
            self._viewer.InteractionOff()
        else:
            if self.angle_widget:
                self.angle_widget.hide()
                # Включаем обычное взаимодействие для виджета
                self._viewer.InteractionOn()

    @pyqtSlot(bool)
    def on_toolButtonLineProbe_toggled(self, toggle):
        log = open('C:/Users/Public/Documents/log_file.txt', 'a')
        log.write('Построить гистограмму' + '\n')
        log.close()
        self.histogramModel.showHistogram(toggle)
        if toggle == True:
            self.line_widget = LineProbe(self.viewport.interactor,
                                         self._viewer.GetProp3D(),
                                         on_changed=self.on_lineprobe)

            self.line_widget.place(self.imageModel.image.bounds,
                                   self._viewer.GetPlaneOrientation(),
                                   self._viewer.GetSlicePosition())

            self.line_widget.show()
            self.line_widget.callback(1, 1)
            # Выключаем обычное взаимодействие для виджета
            self._viewer.InteractionOff()
        else:
            if self.line_widget:
                self.line_widget.hide()
                # Включаем обычное взаимодействие для виджета
                self._viewer.InteractionOn()

    def on_lineprobe(self, probe):
        spline = vtk.vtkSplineFilter()
        spline.SetInputData(probe)
        spline.SetSubdivideToSpecified()
        spline.SetNumberOfSubdivisions(256)
        spline.Update()

        sample_volume = vtk.vtkProbeFilter()
        sample_volume.SetInputData(1, self.imageModel.image)
        sample_volume.SetInputData(0, spline.GetOutput())
        sample_volume.Update()

        samples = sample_volume.GetOutput().GetPointData().GetArray(0)
        samples = np.array([samples.GetValue(i)
                            for i in range(samples.GetNumberOfValues())])

        self.histogramModel.setHistogram(samples)
        # plt.plot(samples)
        # plt.show()


class LineProbe(object):

    def __init__(self, interactor, prop, on_changed=None):
        self.interactor = interactor
        self.on_changed = on_changed

        self.widget = vtk.vtkLineWidget()
        self.widget.SetInteractor(self.interactor)
        self.widget.SetProp3D(prop)
        self.widget.AddObserver(vtk.vtkCommand.EndInteractionEvent,
                                self.callback)

    def place(self, bounds, orientation, position):
        self.widget.PlaceWidget(bounds)

        if orientation == 0:
            self.widget.SetPoint1(position, bounds[2], bounds[5] / 2)
            self.widget.SetPoint2(position, bounds[3], bounds[5] / 2)

        elif orientation == 1:
            self.widget.SetPoint1(bounds[0], position, bounds[5] / 2)
            self.widget.SetPoint2(bounds[1], position, bounds[5] / 2)

        elif orientation == 2:
            self.widget.SetPoint1(bounds[0], bounds[3] / 2, position)
            self.widget.SetPoint2(bounds[1], bounds[3] / 2, position)

    def updateSlice(self, orientation, position):
        p1 = self.widget.GetPoint1()
        p2 = self.widget.GetPoint2()

        if orientation == 0:
            self.widget.SetPoint1(position, p1[1], p1[2])
            self.widget.SetPoint2(position, p2[1], p2[2])

        elif orientation == 1:
            self.widget.SetPoint1(p1[0], position, p1[2])
            self.widget.SetPoint2(p2[0], position, p2[2])

        elif orientation == 2:
            self.widget.SetPoint1(p1[0], p1[1], position)
            self.widget.SetPoint2(p2[0], p2[1], position)

        self.callback(1, 1)

    def as_polydata(self):
        tmp = Mesh()
        self.widget.GetPolyData(tmp)
        return tmp

    def set_on_angle_changed(self, callback):
        self.on_changed = callback

    def callback(self, caller, event):
        if self.on_changed:
            self.on_changed(self.as_polydata())

    def show(self):
        self.widget.On()

    def hide(self):
        self.widget.Off()
