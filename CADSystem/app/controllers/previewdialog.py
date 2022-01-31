import vtk
import numpy

from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import QDialog, QAbstractButton

from libcore.display import PolyActor
from libcore.geometry import Plane
from libcore.widget import LineProbe, DistanceMeasurer

from ..models.image import imageModel
from ..models.view3d import view3dModel
from ..models.layout import LayoutModel, layoutModel
from ..models.editor import editorModel
from ..models.implantor import implantorModel
from ..models.histogram import histogramModel
from ..models.plane import PlaneModel, axialModel, coronalModel, sagittalModel
from ..views.previewdialog_ui import Ui_PreviewDialog


class PreviewDialog(QDialog, Ui_PreviewDialog):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)

        self.setWindowFlags(self.windowFlags() |
                            Qt.WindowMaximizeButtonHint |
                            Qt.WindowMinimizeButtonHint)
        # ~Qt.WindowCloseButtonHint)

        self.dwHistogram_.hide()
        self.lRuler3D.setHidden(True)

        self.imageModel = imageModel

        self.view3dModel = view3dModel
        self.view3dModel.tissueUpdated.connect(self.updateTissue)

        self.layoutModel = layoutModel

        self.editorModel = editorModel

        self.implantorModel = implantorModel

        self.histogramModel = histogramModel
        self.histogramModel.histogramEnabled.connect(
            self.dwHistogram_.setVisible)

        axialModel.sliceUpdated.connect(self.updateAxial)
        sagittalModel.sliceUpdated.connect(self.updateSagittal)
        coronalModel.sliceUpdated.connect(self.updateCoronal)

        self.colormap.loadImage()
        self.updateAxial()
        self.updateSagittal()
        self.updateCoronal()

    def updateAxial(self):
        if self.cbEditor.isChecked():
            for prop in self.editorModel.props:
                actor = self.editorModel.props[prop]

                # axial
                plane_axial = Plane.XY(
                    origin=self.layouts.axial._viewer.GetOrigin())
                clipped = actor.mesh.slice_by_plane(plane=plane_axial)

                if hasattr(self, 'contour_axial'):
                    self.contour_axial.mesh = clipped
                else:
                    self.contour_axial = PolyActor(mesh=clipped,
                                                   color=actor.color,
                                                   render_lines_as_tubes=True,
                                                   line_width=2)
                    self.layouts.axial.viewport.add_prop(self.contour_axial)
        if self.cbImplant.isChecked():
            for prop in self.implantorModel.props:
                actor = self.implantorModel.props[prop]

                # axial
                plane_axial = Plane.XY(
                    origin=self.layouts.axial._viewer.GetOrigin())
                clipped = actor.mesh.slice_by_plane(plane=plane_axial)

                if hasattr(self, 'contour_axial'):
                    self.contour_axial.mesh = clipped
                else:
                    self.contour_axial = PolyActor(mesh=clipped,
                                                   color=actor.color,
                                                   render_lines_as_tubes=True,
                                                   line_width=2)
                    self.layouts.axial.viewport.add_prop(self.contour_axial)

        self.layouts.axial.viewport.rwindow.Render()

    def updateSagittal(self):
        if self.cbEditor.isChecked():
            for prop in self.editorModel.props:
                actor = self.editorModel.props[prop]

                # sagittal
                plane_sagittal = Plane.XZ(
                    origin=self.layouts.sagittal._viewer.GetOrigin())
                clipped = actor.mesh.slice_by_plane(plane=plane_sagittal)

                if hasattr(self, 'contour_sagittal'):
                    self.contour_sagittal.mesh = clipped
                else:
                    self.contour_sagittal = PolyActor(mesh=clipped,
                                                      color=actor.color,
                                                      render_lines_as_tubes=True,
                                                      line_width=2)
                    self.layouts.sagittal.viewport.add_prop(
                        self.contour_sagittal)
        if self.cbImplant.isChecked():
            for prop in self.implantorModel.props:
                actor = self.implantorModel.props[prop]

                # sagittal
                plane_sagittal = Plane.XZ(
                    origin=self.layouts.sagittal._viewer.GetOrigin())
                clipped = actor.mesh.slice_by_plane(plane=plane_sagittal)

                if hasattr(self, 'contour_sagittal'):
                    self.contour_sagittal.mesh = clipped
                else:
                    self.contour_sagittal = PolyActor(mesh=clipped,
                                                      color=actor.color,
                                                      render_lines_as_tubes=True,
                                                      line_width=2)
                    self.layouts.sagittal.viewport.add_prop(
                        self.contour_sagittal)

        self.layouts.sagittal.viewport.rwindow.Render()

    def updateCoronal(self):
        if self.cbEditor.isChecked():
            for prop in self.editorModel.props:
                actor = self.editorModel.props[prop]

                # coronal
                plane_coronal = Plane.YZ(
                    origin=self.layouts.coronal._viewer.GetOrigin())
                clipped = actor.mesh.slice_by_plane(plane=plane_coronal)

                if hasattr(self, 'contour_coronal'):
                    self.contour_coronal.mesh = clipped
                else:
                    self.contour_coronal = PolyActor(mesh=clipped,
                                                     color=actor.color,
                                                     render_lines_as_tubes=True,
                                                     line_width=2)
                    self.layouts.coronal.viewport.add_prop(
                        self.contour_coronal)
        if self.cbImplant.isChecked():
            for prop in self.implantorModel.props:
                actor = self.implantorModel.props[prop]

                # coronal
                plane_coronal = Plane.YZ(
                    origin=self.layouts.coronal._viewer.GetOrigin())
                clipped = actor.mesh.slice_by_plane(plane=plane_coronal)

                if hasattr(self, 'contour_coronal'):
                    self.contour_coronal.mesh = clipped
                else:
                    self.contour_coronal = PolyActor(mesh=clipped,
                                                     color=actor.color,
                                                     render_lines_as_tubes=True,
                                                     line_width=2)
                    self.layouts.coronal.viewport.add_prop(
                        self.contour_coronal)

        self.layouts.coronal.viewport.rwindow.Render()

    @pyqtSlot(QAbstractButton, bool)
    def on_buttonGroupLayouts_buttonToggled(self, btn, toggle):
        if toggle == True:
            if btn == self.tbLayoutClassicRight:
                self.layoutModel.state = LayoutModel.CLASSIC_RIGHT
            elif btn == self.tbLayoutClassicBottom:
                self.layoutModel.state = LayoutModel.CLASSIC_BOTTOM
            elif btn == self.tbLayoutTwoByTwo:
                self.layoutModel.state = LayoutModel.TWO_BY_TWO
            elif btn == self.tbLayoutOnly3D:
                self.layoutModel.state = LayoutModel.ONLY_3D
            elif btn == self.tbLayoutOnlyAxial:
                self.layoutModel.state = LayoutModel.ONLY_AXIAL
            elif btn == self.tbLayoutOnlySagittal:
                self.layoutModel.state = LayoutModel.ONLY_SAGITTAL
            elif btn == self.tbLayoutOnlyCoronal:
                self.layoutModel.state = LayoutModel.ONLY_CORONAL

    @pyqtSlot(QAbstractButton, bool)
    def on_buttonGroupTissue_buttonToggled(self, btn, toggle):
        if toggle == True:
            if btn == self.radioButtonBone:
                self.layouts.view3d.actor.tissue = "bone"
                self.layouts.view3d.updateRender()
                self.view3dModel.tissue = view3dModel.TISSUE_BONE
            elif btn == self.radioButtonMuscle:
                self.layouts.view3d.actor.tissue = "muscle"
                self.layouts.view3d.updateRender()
                self.view3dModel.tissue = view3dModel.TISSUE_MUSCLE
            elif btn == self.radioButtonSkin:
                self.layouts.view3d.actor.tissue = "skin"
                self.layouts.view3d.updateRender()
                self.view3dModel.tissue = view3dModel.TISSUE_SKIN

    @pyqtSlot()
    def updateTissue(self):
        if self.view3dModel.mode != view3dModel.MODE_VOLUME:
            return
        print("{} tissue set {}".format(self.objectName(),
                                        self.view3dModel.tissue))

    @pyqtSlot()
    def on_pbClose_pressed(self):
        log = open('C:/Users/Public/Documents/log_file.txt', 'a')
        log.write('Закрыть предпросмотр' + '\n')
        log.close()
        self.hide()

    def on_pb3DRuler_toggled(self, toggle):
        log = open('C:/Users/Public/Documents/log_file.txt', 'a')
        log.write('Включить 3D измеритель' + '\n')
        log.close()
        if toggle:
            self.on_pbHistogram_toggled(False)
            self.lRuler3D.setHidden(False)

            self.widget = vtk.vtkLineWidget2()
            self.widget.SetInteractor(self.layouts.view3d.viewport.interactor)
            self.widget.CreateDefaultRepresentation()
            rep = self.widget.GetLineRepresentation()
            rep.SetPoint2WorldPosition(numpy.array(rep.GetPoint2WorldPosition()) * 50)
            self.widget.GetLineRepresentation().SetDistanceAnnotationFormat("%-#6.3g mm")
            self.widget.GetLineRepresentation().SetDistanceAnnotationVisibility(True)
            self.widget.AddObserver(vtk.vtkCommand.EndInteractionEvent,
                                    self.ruler3d_callback)
            self.ruler3d_callback(None, None)
            self.widget.On()
        else:
            if hasattr(self, 'widget'):
                if hasattr(self.widget, 'Off'):
                    self.widget.Off()
                self.lRuler3D.setHidden(True)

    def ruler3d_callback(self, caller, event):
        distance = self.widget.GetLineRepresentation().GetDistance()
        self.lRuler3D.setText('Длина: {:-f} мм'.format(distance))

    def on_pbHistogram_toggled(self, toggle):
        log = open('C:/Users/Public/Documents/log_file.txt', 'a')
        log.write('Включить гистограмму'+'\n')
        log.close()
        self.histogramModel.showHistogram(toggle)
        if toggle:
            self.on_pb3DRuler_toggled(False)

            self.lineprobe = LineProbe(self.layouts.view3d.viewport.interactor,
                                       self.layouts.view3d.actor,
                                       on_changed=self.histogramModel.setHistogram)
            self.lineprobe.image = self.imageModel.image
            self.lineprobe.place(self.imageModel.image.bounds)
            self.lineprobe.callback(1, 1)
            self.lineprobe.show()
        else:
            if hasattr(self, 'lineprobe'):
                self.lineprobe.hide()
