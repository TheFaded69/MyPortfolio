from libcore.mesh import Mesh
from libcore.mixins import ViewportMixin
from libcore.display import PolyActor
from libcore.geometry import point_distance

IMPLANTS = ['../data/PBL-102.STL',
            '../data/PBR-102.STL']


def fit_implant(implant, bone, nx=5, ny=5, nz=1):
    # Для каждого бокса
    result = implant.copy()
    boxes = implant.subboxes(nx=nx, ny=ny, nz=nz)

    for box in boxes:
        implant_points_idxs = implant.points_in_box(box)
        bone_points_idxs = bone.points_in_box(box)
        if (len(implant_points_idxs) > 0) and (len(bone_points_idxs) > 0):
            # Найти точку для которой наименьшее расстояние
            min_dist = 100000.0
            for implant_pt in implant.points[implant_points_idxs]:
                for bone_pt in bone.points[bone_points_idxs]:
                    distance = point_distance(implant_pt, bone_pt)
                    if distance < min_dist:
                        min_dist = distance
                        vec = implant_pt - bone_pt
            result.points[implant_points_idxs] -= vec
    result.Modified()
    return result


class App(ViewportMixin):

    def __init__(self):
        super().__init__()
        NX, NY, NZ = 20, 5, 1

        self.bone = Mesh('../../data/rooster.midres.stl')
        self.implant = Mesh('../data/l.stl')
        self.implant.rotate_x(-60.0, inplace=True)
        self.implant.move(55, 40, 190, inplace=True)
        # Увеличиваем количество точек в меше
        #self.implant.subdivide(levels=3, algorithm='butterfly', inplace=True)
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