from libcore.mesh import Mesh

if __name__ == '__main__':
    print('l')
    implant = Mesh('../data/PBL-102.STL')
    implant.resample(nx=140, ny=130, nz=100, value=0.0, inplace=True)
    implant.reverse_sense(inplace=True)
    implant.save('../data/l.stl')
    print('done l')

    print('r')
    implant = Mesh('../data/PBR-102.STL')
    implant.resample(nx=140, ny=130, nz=100, value=0.0, inplace=True)
    implant.reverse_sense(inplace=True)
    implant.save('../data/r.stl')
    print('done r')