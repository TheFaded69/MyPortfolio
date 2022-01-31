# 1. Загрузить изображение
# 2. Построить меш
# 3. Создать и включить трехмерный вариант двумерной штуки
# 4. Сделать реслайсинг как там это было

import vtk
import matplotlib.pyplot as plt
from libcore.mesh import Mesh
from libcore.mixins import ViewportMixin
from libcore.display import PolyActor
from libcore.image import Image
from libcore.widget import LineProbe


class App(ViewportMixin):

    def __init__(self):
        super().__init__()
        # Выбираем стиль взаимодействия
        self.style = vtk.vtkInteractorStyleTrackballCamera()
        # Загружаем изображение
        self.image = Image('../../data/rooster.vti')
        # Извлекаем меш
        self.mesh = self.image.extract_surface(discrete=False)

        self.actor = PolyActor(mesh=self.mesh, color='yellow')
        self.add_prop(self.actor)

        self.register_callback(vtk.vtkCommand.CharEvent, self.on_char)

        self.lineprobe = LineProbe(self.interactor, self.actor, on_changed=self.on_lineprobe)
        self.lineprobe.image = self.image
        #self.lineprobe.place_at_point(self.image.center)
        self.lineprobe.show()

    def on_lineprobe(self, probe):
        plt.plot(probe)
        plt.show()

    def on_char(self, caller, event):
        if event == 'CharEvent':
            key = self.interactor.GetKeySym()
            if key == '1':
                print('1 is pressed')
            elif key == '2':
                print('2 is pressed')

if __name__ == '__main__':
    app = App()
    app.run()