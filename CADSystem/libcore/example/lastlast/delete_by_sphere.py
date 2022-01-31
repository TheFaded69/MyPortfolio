import vtk

from libcore.mesh import Mesh
from libcore.mixins import ViewportMixin
from libcore.display import PolyActor
from libcore.color import get_color
from libcore.widget import Label

class CubeManipulator(object):

    def __init__(self, interactor, actor):
        self.interactor = interactor
        self.actor = actor
        self._transform = vtk.vtkTransform()

        self.widget = vtk.vtkBoxWidget()
        self.widget.SetInteractor(self.interactor)
        self.widget.SetPlaceFactor(1)
        self.widget.AddObserver(vtk.vtkCommand.InteractionEvent, self.event)

    @property
    def transform(self):
        self.widget.GetTransform(self._transform)
        return self._transform

    @property
    def mesh(self):
        return self.actor.mesh.apply_transform(self.transform)

    def event(self, caller, ev):
        self.actor.SetUserTransform(self.transform)

    def show(self):
        self.widget.PlaceWidget(self.actor.GetBounds())
        self.widget.On()

    def hide(self):
        self.widget.Off()


class SphereSelector(object):

    def __init__(self, interactor, mesh):
        self.interactor = interactor
        self.original = mesh
        self.current = None

        self.ghost = PolyActor(self.original, color='white', opacity=0.1)
        self.precut = PolyActor(self.original, color='red', opacity=1.0)

        self.renderer.AddActor(self.ghost)
        self.renderer.AddActor(self.precut)

        # self.mesh_actor = PolyActor(self.original, color='blue', line_width=2.0)
        self.widget = vtk.vtkBoxWidget()
        self.widget.SetInteractor(interactor)
        self.widget.SetProp3D(self.precut)
        self.widget.PlaceWidget(self.original.bounds)

        self.widget.GetFaceProperty().SetEdgeColor(get_color('blue'))
        self.widget.GetSelectedFaceProperty().SetEdgeColor(get_color('yellow'))

        self.widget.AddObserver(vtk.vtkCommand.InteractionEvent, self.event)
        self.label = Label(self.interactor, text='')
        self.event(caller=None, ev=None)

    def event(self, caller, ev):
        self.current = self.original.clip_by_mesh(self.as_polydata())
        self.precut.mesh = self.current

        trans = vtk.vtkTransform()
        self.widget.GetTransform(trans)
        sx, sy, sz = trans.GetScale()
        bounds = self.original.bounds

        width = (bounds[1] - bounds[0])*sx
        height = (bounds[3] - bounds[2])*sy
        depth = (bounds[5] - bounds[4])*sz
        self.label.text = '{}\n{}\n{}'.format(width, height, depth)

    def callback(self, caller, ev):
        print

    @property
    def renderer(self):
        return self.interactor.GetRenderWindow().GetRenderers().GetFirstRenderer()

    def show(self):
        self.widget.On()

    def hide(self):
        self.widget.Off()

    def as_polydata(self):
        poly_data = vtk.vtkPolyData()
        self.widget.GetPolyData(poly_data)
        return poly_data

    def as_planes(self):
        planes = vtk.vtkPlanes()
        self.widget.GetPlanes(planes)
        return planes


class App(ViewportMixin):

    def __init__(self):
        super().__init__()
        self.mesh = Mesh('../../data/rooster.midres.stl')
        self.sphere_selector = SphereSelector(interactor=self.interactor,
                                              mesh=self.mesh)
        self.sphere_selector.show()

        self.register_callback(vtk.vtkCommand.CharEvent, self.on_char)

    def on_char(self, caller, event):
        char = self.interactor.GetKeySym()
        if char == '1':
            print('One was pressed')
        elif char == '2':
            print('Two was pressed')


app = App()
app.run()