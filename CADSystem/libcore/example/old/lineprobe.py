import vtk
import numpy as np

import matplotlib.pyplot as plt

from libcore.image import Image
from libcore.mesh import Mesh
from libcore.mixins import ViewportMixin
from libcore.widget import LineProbe




class App(ViewportMixin):
    def __init__(self):
        super().__init__()
        self.style = vtk.vtkInteractorStyleTrackballCamera()
        self.image = Image()
        self.image.load('../data/hip.vti')

        self.plane_widget = vtk.vtkImagePlaneWidget()
        self.plane_widget.DisplayTextOn()
        self.plane_widget.SetInputData(self.image)
        self.plane_widget.SetPlaneOrientation(2)
        self.plane_widget.SetSliceIndex(int(self.image.depth/2))
        self.plane_widget.SetInteractor(self.interactor)
        self.plane_widget.On()

        self.plane_widget.SetInteraction(0)

        self.lineprobe = LineProbe(self.interactor, self.plane_widget.GetProp3D(), on_changed=self.on_lineprobe)
        self.lineprobe.place_at_point(self.image.center)
        print(self.image.center)
        self.lineprobe.show()
        self.register_callback(vtk.vtkCommand.CharEvent, self.event)

    def event(self, caller, ev):
        key = self.interactor.GetKeySym()
        if key == '1':
            self.plane_widget.SetPlaneOrientationToXAxes()
        elif key == '2':
            self.plane_widget.SetPlaneOrientationToYAxes()
        elif key == '3':
            self.plane_widget.SetPlaneOrientationToZAxes()
        elif key == 'a':
            self.look_ap()
        elif key == 's':
            self.look_inf()
        elif key == 'd':
            self.look_lao()
        elif key == 'f':
            self.look_ll()
        elif key == 'g':
            self.look_pa()
        elif key == 'h':
            self.look_sup()
        self.rwindow.Render()

    def on_lineprobe(self, probe):

        plt.plot(probe)
        plt.show()

app = App()
app.run()