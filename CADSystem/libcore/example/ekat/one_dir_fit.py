"""
Алгоритм нужен следующий:
1. Ориентируем нужным образом имплант относительно кости
2. Разбиваем имплант на боксы. Только в самом длинном направлении.
3. В каждом боксе берем центральную часть
4. Если точек нет - то NAN
5. Считаем для каждого бокса вектор смещения
6. Заполняем по соседям
7. Фильтруем вектора по 5 соседям
8. Применяем вектора
"""

import vtk
import numpy as np
from libcore.mesh import Mesh
from libcore.mixins import ViewportMixin
from libcore.display import PolyActor
from libcore.geometry import point_distance

IMPLANTS = ['../data/l.STL',
            '../data/r.STL']

def fit_implant(implant, bone, steps=20):
    boxes = implant.subboxes(nx=steps, ny=1, nz=1)

    center_boxes = []
    for box in boxes:
        sub_boxes = box.subboxes(nx=1, ny=5, nz=1, oversize='z')
        center_boxes.append(sub_boxes[1])

    displacement_vectors = []
    for box in center_boxes:
        vec = None
        implant_idxs = implant.points_in_box(box)
        bone_idxs = bone.points_in_box(box)

        # Только непустые
        if (len(implant_idxs) > 0) and (len(bone_idxs) > 0):
            # Найти точку для которой наименьшее расстояние
            vec = None
            min_dist = 100000.0
            for pt_implant in implant.points[implant_idxs]:
                for pt_bone in bone.points[bone_idxs]:
                    distance = point_distance(pt_implant, pt_bone)
                    if distance < min_dist:
                        min_dist = distance
                        vec = pt_implant - pt_bone
        displacement_vectors.append(vec)

    for idx in range(1, len(displacement_vectors)):
        if displacement_vectors[idx] is None:
            displacement_vectors[idx] = displacement_vectors[idx-1]

    filtered = []
    filtered.append(displacement_vectors[0])
    for idx in range(len(displacement_vectors) - 3 + 1):
        win = displacement_vectors[idx:(idx + 3)]
        sample = (win[0] + win[1] + win[2]) / 3
        filtered.append(sample)
    filtered.append(displacement_vectors[-1])


    result = implant.copy()
    for box, vec in zip(boxes, displacement_vectors):
        insiders = implant.points_in_box(box)
        result.points[insiders] -= vec
    result.Modified()
    return result


class App(ViewportMixin):

    def __init__(self):
        super().__init__()

        self.bone = Mesh('../../data/rooster.midres.stl')
        self.implant = Mesh('../data/l.stl')
        self.implant.rotate_x(-60.0, inplace=True)
        self.implant.move(55, 40, 190, inplace=True)

        self.fitted = fit_implant(implant=self.implant,
                                  bone=self.bone,
                                  steps=30)
        self.fitted.save('fitted.stl')


        self.add_prop(PolyActor(self.bone, color='white'))
        self.add_prop(PolyActor(self.implant, color='red', opacity=0.5))
        self.add_prop(PolyActor(self.fitted, color='blue', opacity=0.5))


if __name__ == '__main__':
    app = App()
    app.run()
