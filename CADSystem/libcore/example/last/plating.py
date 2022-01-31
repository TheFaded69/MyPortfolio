# Построение пластинки
import vtk
import numpy as np

from libcore.mixins import ViewportMixin
from libcore.display import PolyActor
from libcore.mesh import Mesh

from libcore.topology import cell_neighbors
from libcore.topology import points_ids_within_radius
from libcore.topology import face_for_point
from libcore.topology import points_for_face
from libcore.topology import find_geodesic


# spline = vtk.vtkSplineFilter()
# spline.SetInputData(self.as_polydata())
# spline.SetSubdivideToSpecified()
# spline.SetNumberOfSubdivisions(256)
# spline.Update()


class SurfaceProbe(object):

    def __init__(self, interactor, mesh, actor, on_changed=None):
        self.interactor = interactor
        self.on_changed = on_changed
        self.mesh = mesh

        self.sphere = vtk.vtkSphereSource()
        self.sphere.SetRadius(5)
        self.sphere.Update()

        self.point_placer = vtk.vtkPolygonalSurfacePointPlacer()
        # self.point_placer.GetPolys().AddItem(self.sphere.GetOutput())
        self.point_placer.GetPolys().AddItem(mesh)
        self.point_placer.AddProp(actor)
        self.point_placer.SnapToClosestPointOn()
        # print('Interpolator', self.point_placer.GetLineInterpolator())

        self.widget = vtk.vtkContourWidget()
        self.widget.SetInteractor(interactor)
        self.representation = self.widget.GetRepresentation()
        self.representation.GetLinesProperty().SetColor(1, 0, 0)
        self.representation.GetLinesProperty().SetLineWidth(0.0)
        self.representation.SetPointPlacer(self.point_placer)
        self.widget.AddObserver(vtk.vtkCommand.InteractionEvent, self.callback)

    @property
    def curve(self):
        polydata = Mesh(self.representation.GetContourRepresentationAsPolyData())
        original_points = polydata.points
        new_points = []

        for i in range(1, len(original_points)):
            geodesic_mesh = find_geodesic(self.mesh,
                                          self.mesh.find_closest_point(original_points[i - 1]),
                                          self.mesh.find_closest_point(original_points[i]))
            for pt in geodesic_mesh.points:
                new_points.append(list(pt))
        return Mesh.from_points(new_points)

    def callback(self, caller, event):
        # print("There are ", self.representation.GetNumberOfNodes(), " nodes.")

        if self.on_changed:
            self.on_changed()

    def show(self):
        self.widget.On()

    def hide(self):
        self.widget.Off()


class App(ViewportMixin):

    def __init__(self):
        super().__init__()

        self.mesh = Mesh('../../data/rooster.midres.stl')
        self.actor = PolyActor(mesh=self.mesh, color='white', edge_visibility=True)
        self.add_prop(self.actor)

        self.curve_actor = None

        self.curve = SurfaceProbe(interactor=self.interactor,
                                  mesh=self.mesh,
                                  actor=self.actor,
                                  on_changed=self.on_curve)
        self.curve.show()
        self.register_callback(vtk.vtkCommand.CharEvent, self.on_char)

    def on_char(self, caller, event):
        key = self.interactor.GetKeySym()
        if key == '1':
            print('something with curve)')
            mesh = self.curve.curve
            print(mesh.points)
            if self.curve_actor:
                self.remove_prop(self.curve_actor)
            self.curve_actor = PolyActor(mesh=self.curve.curve, line_width=4.0, color='blue', edge_visibility=True,
                                         point_size=5, render_points_as_spheres=True)
            self.add_prop(self.curve_actor)

            self.rwindow.Render()
        elif key == '2':
            print('2')

    def on_curve(self):
        # if self.curve_actor:
        #     self.remove_prop(self.curve_actor)
        # self.curve_actor = PolyActor(mesh=self.curve.curve, line_width=4.0, color='blue', edge_visibility=True)
        # self.add_prop(self.curve_actor)
        pass


app = App()
app.run()