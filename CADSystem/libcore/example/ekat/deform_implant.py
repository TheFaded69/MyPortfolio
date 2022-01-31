import vtk
import numpy as np

from libcore.mesh import Mesh
from libcore.mixins import ViewportMixin
from libcore.display import PolyActor
from libcore.widget import CubeManipulator
from libcore.geometry import fit_implant

IMPLANTS = ['../data/PBL-102.STL',
            '../data/PBR-102.STL']


class App(ViewportMixin):

    def __init__(self):
        super().__init__()

        self.skull_mesh = Mesh('../../data/rooster.hires.stl')
        self.implant_mesh = Mesh(IMPLANTS[0])
        self.implant_mesh.subdivide(levels=2, algorithm='linear', inplace=True)

        self.skull_actor = PolyActor(mesh=self.skull_mesh,
                                     color='white',
                                     opacity=1.0)

        self.implant_actor = PolyActor(mesh=self.implant_mesh,
                                       color='peacock',
                                       edge_color='black',
                                       edge_visibility=True,
                                       opacity=1.0)

        self.add_prop(self.implant_actor)
        self.add_prop(self.skull_actor)
        self.cube_manip = CubeManipulator(self.interactor, self.implant_actor, scaling=False)
        self.cube_manip.show()
        self.register_callback(vtk.vtkCommand.CharEvent, self.proc_char)

        self.result_actor = None

    def proc_char(self, caller, event):
        key = self.interactor.GetKeySym()
        print('{} was pressed'.format(key))
        if key == '1':
            mesh = self.cube_manip.mesh
            fitted = fit_implant(implant=mesh,
                                 bone=self.skull_mesh)
            if self.result_actor:
                self.remove_prop(self.result_actor)

            self.result_actor = PolyActor(fitted, color='red')
            self.add_prop(self.result_actor)

        if key == '2':
            print(self.cube_manip.transform)


if __name__ == '__main__':
    app = App()
    app.run()