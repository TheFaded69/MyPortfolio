import numpy as np

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from PyQt5.QtWidgets import QWidget, QSizePolicy

from ..models.histogram import histogramModel

from ..views.histogram_ui import Ui_Histogram


class Histogram(QWidget, Ui_Histogram):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)

        self.plot = PlotCanvas(self)
        self.layout.addWidget(self.plot)

        self.histogramModel = histogramModel
        self.histogramModel.histogramUpdated.connect(self.updateSamples)

    def updateSamples(self):
        self.plot.plot(self.histogramModel.histogram)


class PlotCanvas(FigureCanvas):

    def __init__(self, parent=None, width=4, height=5, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def plot(self, x):
        self.axes.clear()
        self.axes.plot(x)
        self.axes.plot([500] * len(x))
        self.draw()
