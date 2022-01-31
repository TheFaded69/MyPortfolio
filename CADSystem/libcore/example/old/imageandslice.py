import vtk

from libcore.mesh import Mesh
from libcore.image import Image
from libcore.mixins import ViewportMixin
from libcore.display import PolyActor
from libcore.geometry import Plane

class App(ViewportMixin):

    def __init__(self):
        super().__init__()

        image = Image('../data/rooster.vti')
        self.original = Mesh('../data/rooster.midres.stl')
        self.original.compute_normals()
        self.add_prop(PolyActor(mesh=self.original, color='white'))

        plane = Plane.XY(origin=self.original.center)
        clipped = self.original.slice_by_plane(plane=plane)
        self.contour = PolyActor(mesh=clipped, color='red', render_lines_as_tubes=True, line_width=3)
        self.add_prop(self.contour)

        self.widget = vtk.vtkImagePlaneWidget()
        self.widget.SetInteractor(self.interactor)
        self.widget.SetInputData(image)
        self.widget.SetPlaneOrientationToZAxes()
        self.widget.DisplayTextOn()
        self.widget.SetRestrictPlaneToVolume(True)
        self.widget.SetResliceInterpolateToNearestNeighbour()
        self.widget.On()
        self.widget.SetRightButtonAction(vtk.vtkImagePlaneWidget.VTK_SLICE_MOTION_ACTION)
        self.widget.SetMiddleButtonAction(vtk.vtkImagePlaneWidget.VTK_WINDOW_LEVEL_ACTION)

        self.widget.AddObserver(vtk.vtkCommand.InteractionEvent, self.on_end_interaction)

    def on_end_interaction(self, caller, event):
        plane = Plane.XY(origin=self.widget.GetOrigin())
        clipped = self.original.slice_by_plane(plane=plane)
        self.contour.mesh = clipped

if __name__ == '__main__':
    app = App()
    app.run()
