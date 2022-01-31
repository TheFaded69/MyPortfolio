from random import random

import vtk

from libcore.mesh import Mesh
from libcore.display import PolyActor
from libcore.mixins import ViewportMixin


class SphereWidget(vtk.vtkSphereWidget):

    def __init__(self, interactor, center=(0, 0, 0), radius=5.0):
        super().__init__()
        self.interactor = interactor

        self.picker = vtk.vtkWorldPointPicker()
        self.interactor.SetPicker(self.picker)
        self.SetInteractor(self.interactor)
        self.SetRepresentationToSurface()
        self.GetSphereProperty().SetColor(0, 1, 0)
        self.GetSelectedSphereProperty().SetColor(0, 1, 1)

        self.center = center
        self.radius = radius
        self.RemoveAllObservers()
        self.interactor.AddObserver(vtk.vtkCommand.MouseMoveEvent, self.OnMouseMove)

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

    def as_mesh(self):
        polydata = vtk.vtkPolyData()
        self.GetPolyData(polydata)
        return Mesh(polydata)

    def as_sphere(self):
        sphere = vtk.vtkSphere()
        self.GetSphere(sphere)
        return sphere

    def OnMouseMove(self, caller, event):
        print('OnMouseMove')
        #super().OnMouseMove()
        dx, dy = self.interactor.GetEventPosition()
        self.picker.Pick(dx, dy, 0, self.renderer)
        x, y, z = self.picker.GetPickPosition()
        self.center = (x, y, z)


    def show(self):
        self.On()

    def hide(self):
        self.Off()



class App(ViewportMixin):

    def __init__(self):
        super().__init__()

        self.mesh = Mesh('../../data/rooster.midres.stl')

        vecs = []
        for i in range(self.mesh.number_of_points):
            vecs.append((0.1*random(), 0.1*random(), 0.1*random()))

        self.mesh.warp(self.mesh, inplace=True)

        self.actor = PolyActor(mesh=self.mesh, color='red')
        self.add_prop(self.actor)

    
app = App()
app.run()