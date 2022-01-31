from libcore.mesh import Mesh
from libcore.mixins import ViewportMixin
from libcore.display import PolyActor
from libcore.geometry import fit_implant

IMPLANTS = ['../data/PBL-102.STL',
            '../data/PBR-102.STL']


class App(ViewportMixin):

    def __init__(self):
        super().__init__()
        NX, NY, NZ = 7, 7, 1

        self.bone = Mesh('../../data/rooster.midres.stl')
        self.implant = Mesh('../data/PBL-102.STL')
        self.implant.rotate_x(-60.0, inplace=True)
        self.implant.move(55, 40, 190, inplace=True)
        # Увеличиваем количество точек в меше
        self.implant.subdivide(levels=3, algorithm='linear', inplace=True)
        # Разбиение ограничивающего параллепипеда
        boxes = self.implant.subboxes(nx=NX, ny=NY, nz=NZ)

        self.fitted = fit_implant(implant=self.implant,
                                  bone=self.bone,
                                  nx=NX,
                                  ny=NY,
                                  nz=NZ)

        self.fitted.save('fitted.stl')

        self.add_prop(PolyActor(self.bone, color='white'))
        self.add_prop(PolyActor(self.implant, color='red', opacity=0.5))
        self.add_prop(PolyActor(self.fitted, color='blue', opacity=0.5))
        for box in boxes:
            self.add_prop(PolyActor(box.outline, color='black'))




if __name__ == '__main__':
    app = App()
    app.run()