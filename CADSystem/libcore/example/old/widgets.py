import vtk
from libcore import Image
from libcore.display import VolActor
from libcore.mixins import ViewportMixin
from libcore.widget import Label
from libcore.widget import Slider
from libcore.widget import DistanceMeasurer
from libcore.widget import AngleMeasurer
from libcore.widget import TextButton

class App(ViewportMixin):

    def __init__(self):
        super().__init__()

        self.style = vtk.vtkInteractorStyleTrackballActor()
        self.image = Image('../data/rooster.vti')
        self.actor = VolActor(self.image)
        self.add_prop(self.actor)

        self.register_callback(vtk.vtkCommand.CharEvent, self.event)

        self.label_left_top = Label(self.interactor, text='This is top left', pos=(0, self.height-24), color='black', fontsize=22)
        self.label_right_top = Label(self.interactor, text='Right')
        self.label_right_top.pos = (self.width - self.label_right_top.width - 5, self.height - self.label_right_top.height - 5)
        self.label_right_bottom = Label(self.interactor, text='Right bottom')
        self.label_right_bottom.pos = (self.width - self.label_right_bottom.width - 5,
                                       5)
        self.label_right_bottom.color = 'green'

        self.button = TextButton(self.interactor)
        self.angle_measurer = AngleMeasurer(self.interactor, on_angle_changed=self.on_measure)
        self.distance_measurer = DistanceMeasurer(self.interactor, on_distance_changed=self.on_measure)
        for d in dir(self.angle_measurer.widget):
            print(d)

    def on_measure(self, value):
        self.label_left_top.text = str(value)

    def on_first_button_click(self):
        self.label_right_bottom.color = 'blue'

    def event(self, caller, ev):
        key = self.interactor.GetKeySym()
        if key == 'a':
            if self.label_left_top.is_visible:
                self.label_left_top.hide()
            else:
                self.label_left_top.show()
        elif key == 's':
            self.label_left_top.text = self.label_left_top.text[::-1]
        elif key == '1':
            if self.angle_measurer.is_visible:
                self.angle_measurer.hide()
            else:
                self.angle_measurer.show()
        elif key == '2':
            if self.distance_measurer.is_visible:
                self.distance_measurer.hide()
            else:
                self.distance_measurer.show()

        self.rwindow.Render()

app = App()
app.run()
