import vtk

from libcore.mixins import ViewportMixin
from libcore.display import PolyActor
from libcore.mesh import Mesh

if __name__ == '__main__':
    files = ['1.stl']

    for file in files:
        print('load {}'.format(file))
        mesh = Mesh('data/{}'.format(file))
        mesh2 = mesh.reflect(plane='x')
        print('save {}'.format(file))
        mesh2.save('out/{}'.format(file))
