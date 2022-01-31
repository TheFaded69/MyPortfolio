import vtk
from libcore.mesh import Mesh
from libcore.mixins import ViewportMixin
from libcore.display import PolyActor
from libcore.color import random_color

IMPLANTS = ['../data/PBL-102.STL',
            '../data/PBR-102.STL']

RED = (255, 0, 0)
GREEN = (0, 255, 0)


class App(ViewportMixin):

    def __init__(self):
        super().__init__()

        self.implant = Mesh('../data/l.stl')
        print(self.implant.bounds)

        self.colors = vtk.vtkUnsignedCharArray()
        self.colors.SetNumberOfComponents(3)
        self.colors.SetName("Colors")

        for idx, pt in enumerate(self.implant.points):
            x, y, z = pt
            if y < 3.1:
                self.colors.InsertNextTuple(RED)
            else:
                self.colors.InsertNextTuple(GREEN)



        self.implant.GetPointData().SetScalars(self.colors)

        self.actor = PolyActor(self.implant,
                               edge_visibility=True,
                               edge_color='black',
                               scalar_visibility=True,
                               render_points_as_spheres=True,
                               point_size=3.0)

        self.add_prop(self.actor)


if __name__ == '__main__':
    app = App()
    app.run()