import random

import vtk
from libcore import Mesh
from libcore import widget
from libcore.mixins import ViewportMixin
from libcore.display import PolyActor


def make_a_mess():
    files = ['../data/ant.stl']
    meshes = list()
    for file in files:
        meshes.append(Mesh(file))

    for i in range(10):
        meshes.append(Mesh.sphere(center=(100*random.random()-50, 150*random.random()-75, 150*random.random()-50),
                                  radius=5*random.random(),
                                  resolution_phi=random.randint(8, 30),
                                  resolution_theta=random.randint(8, 30)))

    mesh = Mesh.from_meshes(meshes_list=meshes)
    return mesh

class App(ViewportMixin):

    def __init__(self):
        super().__init__()
        self.original = make_a_mess()
        self.meshes = self.original.split()
        self.actors = []
        self.show_actors()

        self.slider = widget.Slider(self.interactor,
                                    value=50.0,
                                    minimum_value=0.0,
                                    maximum_value=1000,
                                    caption_text='size',
                                    on_value_changed_callback=self.on_slider)
        self.slider.show()

    def show_actors(self):
        print('show actors')
        for mesh in self.meshes:
            actor = PolyActor(mesh)
            self.add_prop(actor)
            self.actors.append(actor)

    def hide_actors(self):
        print('hide actors')
        for actor in self.actors:
            self.renderer.RemoveActor(actor)
        self.actors = []


    def on_slider(self, val):
        self.meshes = []
        self.hide_actors()

        for size, mesh in self.original.split(return_size=True):
            print(size)
            if size > val:
                self.meshes.append(mesh)
        self.show_actors()


    def run(self):
        self.interactor.Start()

app = App()
app.run()

if __name__ == '__main__':
    app = App()
    app.init()
    app.loop()
