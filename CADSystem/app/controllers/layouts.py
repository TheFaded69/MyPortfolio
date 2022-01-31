from PyQt5.QtWidgets import QWidget

from ..models.layout import LayoutModel, layoutModel

from ..views.layoutswidget_ui import Ui_LayoutsWidget


class LayoutsWidget(QWidget, Ui_LayoutsWidget):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)

        self.layoutModel = layoutModel
        self.layoutModel.stateUpdated.connect(self.update)

    def update(self, size=None):
        if not size:
            size = self.size()
        width, height = size.width(), size.height()
        if self.layoutModel.state == LayoutModel.CLASSIC_BOTTOM:
            self.view3d.move(0, 0)
            self.view3d.setFixedSize(width, 2 * height // 3 - 1.5)
            self.view3d.setHidden(False)

            self.axial.move(0, 2 * height // 3 + 1.5)
            self.axial.setFixedSize(width // 3 - 1.5, height // 3)
            self.axial.setHidden(False)

            self.coronal.move(width // 3 + 1.5, 2 * height // 3 + 1.5)
            self.coronal.setFixedSize(width // 3 - 1.5, height // 3)
            self.coronal.setHidden(False)

            self.sagittal.move(2 * width // 3 + 3, 2 * height // 3 + 1.5)
            self.sagittal.setFixedSize(width // 3 - 1.5, height // 3)
            self.sagittal.setHidden(False)

        elif self.layoutModel.state == LayoutModel.CLASSIC_RIGHT:
            self.view3d.move(0, 0)
            self.view3d.setFixedSize(2 * width // 3 - 1.5, height)
            self.view3d.setHidden(False)

            self.axial.move(2 * width // 3 + 1.5, 0)
            self.axial.setFixedSize(width // 3, height // 3 - 1.5)
            self.axial.setHidden(False)

            self.coronal.move(2 * width // 3 + 1.5, height // 3 + 1.5)
            self.coronal.setFixedSize(width // 3, height // 3 - 1.5)
            self.coronal.setHidden(False)

            self.sagittal.move(2 * width // 3 + 1.5, 2 * height // 3 + 1.5)
            self.sagittal.setFixedSize(width // 3, height // 3 - 1.5)
            self.sagittal.setHidden(False)

        elif self.layoutModel.state == LayoutModel.TWO_BY_TWO:
            self.view3d.move(0, 0)
            self.view3d.setFixedSize(width // 2 - 1.5, height // 2 - 1.5)
            self.view3d.setHidden(False)

            self.axial.move(width // 2 + 1.5, 0)
            self.axial.setFixedSize(width // 2 - 1.5, height // 2 - 1.5)
            self.axial.setHidden(False)

            self.coronal.move(0, height // 2 + 1.5)
            self.coronal.setFixedSize(width // 2 - 1.5, height // 2 - 1.5)
            self.coronal.setHidden(False)

            self.sagittal.move(width // 2 + 1.5, height // 2 + 1.5)
            self.sagittal.setFixedSize(width // 2 - 1.5, height // 2 - 1.5)
            self.sagittal.setHidden(False)

        elif self.layoutModel.state == LayoutModel.ONLY_3D:
            self.view3d.move(0, 0)
            self.view3d.setFixedSize(size)
            self.view3d.setHidden(False)

            self.sagittal.setHidden(True)

            self.axial.setHidden(True)

            self.coronal.setHidden(True)

        elif self.layoutModel.state == LayoutModel.ONLY_AXIAL:
            self.axial.move(0, 0)
            self.axial.setFixedSize(size)
            self.axial.setHidden(False)

            self.sagittal.setHidden(True)

            self.view3d.setHidden(True)

            self.coronal.setHidden(True)

        elif self.layoutModel.state == LayoutModel.ONLY_CORONAL:
            self.coronal.move(0, 0)
            self.coronal.setFixedSize(size)
            self.coronal.setHidden(False)

            self.sagittal.setHidden(True)

            self.view3d.setHidden(True)

            self.axial.setHidden(True)

        elif self.layoutModel.state == LayoutModel.ONLY_SAGITTAL:
            self.sagittal.move(0, 0)
            self.sagittal.setFixedSize(size)
            self.sagittal.setHidden(False)

            self.axial.setHidden(True)

            self.view3d.setHidden(True)

            self.coronal.setHidden(True)

        elif self.layoutModel.state == LayoutModel.MIRRORING:
            self.view3d.move(0, 0)
            self.view3d.setFixedSize(size)
            self.view3d.setHidden(False)

            self.sagittal.setHidden(True)

            self.axial.setHidden(True)

            self.coronal.setHidden(True)

    def resizeEvent(self, event):
        self.update(event.size())
        return super().resizeEvent(event)
