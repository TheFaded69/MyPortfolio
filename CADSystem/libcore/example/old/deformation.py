import vtk
import numpy as np


# # This does the actual work.
# # Callback for the interaction
# def callback(caller, event):
#     lineWidget = caller
#
#     # Get the actual box coordinates of the line
#     polydata = vtk.vtkPolyData()
#     rep = caller.GetRepresentation()
#     rep.GetPolyData(polydata)
#     p = [0.0, 0.0, 0.0]
#
#     # Display one of the points, just so we know it's working
#     polydata.GetPoint(0, p)
#     print('P: {} {} {}'.format(p[0], p[1], p[2]))
#
#
# def main():
#     sphereSource = vtk.vtkSphereSource()
#     sphereSource.Update()
#
#     # Create a mapper and actor
#     mapper = vtk.vtkPolyDataMapper()
#     mapper.SetInputConnection(sphereSource.GetOutputPort())
#     actor = vtk.vtkActor()
#     actor.SetMapper(mapper)
#
#     # A renderer and render window
#     renderer = vtk.vtkRenderer()
#     renderWindow = vtk.vtkRenderWindow()
#     renderWindow.AddRenderer(renderer)
#
#     # An interactor
#     renderWindowInteractor = vtk.vtkRenderWindowInteractor()
#     renderWindowInteractor.SetRenderWindow(renderWindow)
#
#     lineWidget = vtk.vtkLineWidget2()
#     lineWidget.SetInteractor(renderWindowInteractor)
#     lineWidget.CreateDefaultRepresentation()
#
#     for d in dir(lineWidget.GetLineRepresentation()):
#         print(d)
#
#     # You could do this if you want to set properties at this point:
#     lineWidget.AddObserver(vtk.vtkCommand.InteractionEvent, callback)
#
#     # Render
#     renderWindow.Render()
#     renderWindowInteractor.Initialize()
#     renderWindow.Render()
#     lineWidget.On()
#
#     # Begin mouse interaction
#     renderWindowInteractor.Start()

#
# class LineProbe(object):
#
#     def __init__(self, interactor, prop, on_changed=None):
#         self.interactor = interactor
#         self.on_changed = on_changed
#
#         self.widget = vtk.vtkLineWidget()
#         self.widget.SetInteractor(self.interactor)
#         self.widget.SetProp3D(prop)
#         self.widget.AddObserver(vtk.vtkCommand.EndInteractionEvent, self.callback)
#
#     def place(self, bounds):
#         self.widget.PlaceWidget(bounds)
#
#     def place_at_point(self, pt):
#         x, y, z = pt
#         self.widget.SetPoint1(x-0.1, y-0.1, z)
#         self.widget.SetPoint2(x+0.1, y+0.1, z)
#
#     def as_polydata(self):
#         tmp = Mesh()
#         self.widget.GetPolyData(tmp)
#         return tmp
#
#     def set_on_angle_changed(self, callback):
#         self.on_changed = callback
#
#     def callback(self, caller, event):
#         spline = vtk.vtkSplineFilter()
#         spline.SetInputData(self.as_polydata())
#         spline.SetSubdivideToSpecified()
#         spline.SetNumberOfSubdivisions(256)
#         spline.Update()
#
#         sample_volume = vtk.vtkProbeFilter()
#         sample_volume.SetInputData(1, self.image)
#         sample_volume.SetInputData(0, spline.GetOutput())
#         sample_volume.Update()
#         samples = sample_volume.GetOutput().GetPointData().GetArray(0)
#         samples = np.array([samples.GetValue(i) for i in range(samples.GetNumberOfValues())])
#         if self.on_changed:
#             self.on_changed(samples)
#
#     def show(self):
#         self.widget.On()
#
#     def hide(self):
#         self.widget.Off()

import vtk


# This does the actual work.
# Callback for the interaction
def callback(caller, event):
    lineWidget = caller

    # Get the actual box coordinates of the line
    polydata = vtk.vtkPolyData()
    rep = caller.GetRepresentation()
    rep.GetPolyData(polydata)
    p = [0.0, 0.0, 0.0]

    # Display one of the points, just so we know it's working
    polydata.GetPoint(0, p)
    print('P: {} {} {}'.format(p[0], p[1], p[2]))


def main():
    sphereSource = vtk.vtkSphereSource()
    sphereSource.Update()

    # Create a mapper and actor
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(sphereSource.GetOutputPort())
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    # A renderer and render window
    renderer = vtk.vtkRenderer()
    renderWindow = vtk.vtkRenderWindow()
    renderWindow.AddRenderer(renderer)

    # An interactor
    renderWindowInteractor = vtk.vtkRenderWindowInteractor()
    renderWindowInteractor.SetRenderWindow(renderWindow)

    lineWidget = vtk.vtkLineWidget2()
    lineWidget.SetInteractor(renderWindowInteractor)
    lineWidget.CreateDefaultRepresentation()

    for d in dir(lineWidget.GetLineRepresentation()):
        print(d)

    # You could do this if you want to set properties at this point:
    lineWidget.AddObserver(vtk.vtkCommand.InteractionEvent, callback)

    # Render
    renderWindow.Render()
    renderWindowInteractor.Initialize()
    renderWindow.Render()
    lineWidget.On()

    # Begin mouse interaction
    renderWindowInteractor.Start()


main()
