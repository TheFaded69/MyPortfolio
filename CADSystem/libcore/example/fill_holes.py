from libcore.mesh import Mesh

if __name__ == '__main__':
    files = ['stich_model_one.stl']

    for file in files:
        print('load {}'.format(file))
        mesh = Mesh('data/{}'.format(file))
        print('fill holes...')
        mesh.fill_holes(hole_size=50, inplace=True)
        print('close mesh...')
        mesh.close_mesh(inplace=True)
        print('saving mesh...')
        mesh.save('out/{}'.format(file))
