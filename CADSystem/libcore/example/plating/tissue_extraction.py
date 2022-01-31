import vtk

from libcore import Image
from libcore import widget
from libcore.display import PolyActor
from libcore.mixins import ViewportMixin


class App(ViewportMixin):

    def __init__(self):
        super().__init__()
        style = vtk.vtkInteractorStyleTrackballActor()
        self.image = Image('../data/rooster.vti')

        self.slider_lower = widget.Slider(self.interactor,
                                    value=380.0,
                                    minimum_value=-2048.0,
                                    maximum_value=2048,
                                    caption_text='lower value',
                                    on_value_changed_callback=self.on_lower_value_changed)

        self.slider_higher = widget.Slider(self.interactor,
                                    value=1200.0,
                                    minimum_value=-2048.0,
                                    maximum_value=2048,
                                    caption_text='higher value',
                                    position='top',
                                    on_value_changed_callback=self.on_higher_value_changed)

        self.slider_lower.show()
        self.slider_higher.show()
        self.interactor.AddObserver(vtk.vtkCommand.UserEvent, self.on_user)

    def on_user(self, caller, event):
        self.build_mesh()

    def on_lower_value_changed(self, value):
        print('lower value changed', value)

    def on_higher_value_changed(self, value):
        print('higher value changed', value)

    def build_mesh(self):
        self.mesh = self.image.extract_surface(threshold=self.slider_lower.value,
                                                threshold2=self.slider_higher.value,
                                                discrete=True)
        self.actor = PolyActor(self.mesh)
        self.add_prop(self.actor)

app = App()
app.run()
