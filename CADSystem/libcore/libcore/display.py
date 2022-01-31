import vtk

from . import cmap


class PolyActor(vtk.vtkActor):
    def __init__(self, mesh, color='green', opacity=1.0, ambient=0.0, ambient_color='white', backface_culling=False,
                 diffuse=1.0, diffuse_color='white', edge_color='black', edge_visibility=False, lighting=True,
                 line_width=1.0, point_size=1.0, render_lines_as_tubes=False, render_points_as_spheres=False,
                 representation='surface', specular=0.0, specular_color='white', specular_power=1.0,
                 vertex_color='peacock', vertex_visibility=False, scalar_visibility=False):
        super().__init__()

        self._is_selected = False
        self._mesh = mesh
        self.mapper = vtk.vtkPolyDataMapper()
        self.mapper.SetInputData(self.mesh)
        self.mapper.SetScalarVisibility(scalar_visibility)
        self.SetMapper(self.mapper)
        #self.GetProperty().SetInterpolationToGouraud()

        self.opacity = opacity
        self.ambient = ambient
        self.ambient_color = ambient_color
        self.backface_culling = backface_culling
        self.diffuse = diffuse
        self.diffuse_color = diffuse_color
        self.edge_color = edge_color
        self.edge_visibility = edge_visibility
        self.lighting = lighting
        self.line_width = line_width
        self.point_size = point_size
        self.render_lines_as_tubes = render_lines_as_tubes
        self.render_points_as_spheres = render_points_as_spheres
        self.representation = representation
        self.specular = specular
        self.specular_color = specular_color
        self.specular_power = specular_power
        self.vertex_color = vertex_color
        self.vertex_visibility = vertex_visibility
        self.color = color

    @property
    def mesh(self):
        return self._mesh

    @mesh.setter
    def mesh(self, value):
        self._mesh = value
        self.mapper.SetInputData(self._mesh)
        self.SetMapper(self.mapper)

    @property
    def is_selected(self):
        return self._is_selected

    @is_selected.setter
    def is_selected(self, value):
        self._is_selected = value

    @property
    def scalar_visibility(self):
        return self.mapper.GetScalarVisibility()

    @scalar_visibility.setter
    def scalar_visibility(self, value):
        self.mapper.SetScalarVisibility(value)

    @property
    def color(self):
        return self.GetProperty().GetColor()

    @color.setter
    def color(self, value):
        self.GetProperty().SetColor(cmap.color(value))

    @property
    def opacity(self):
        return self.GetProperty().GetOpacity()

    @opacity.setter
    def opacity(self, value):
        self.GetProperty().SetOpacity(value)

    @property
    def ambient(self):
        return self.GetProperty().GetAmbient()

    @ambient.setter
    def ambient(self, value):
        self.GetProperty().SetAmbient(value)

    @property
    def ambient_color(self):
        return self.GetProperty().GetAmbientColor()

    @ambient_color.setter
    def ambient_color(self, value):
        self.GetProperty().SetAmbientColor(cmap.color(value))

    @property
    def backface_culling(self):
        return self.GetProperty().GetBackfaceCulling()

    @backface_culling.setter
    def backface_culling(self, value):
        self.GetProperty().SetBackfaceCulling(value)

    @property
    def diffuse(self):
        return self.GetProperty().GetDiffuse()

    @diffuse.setter
    def diffuse(self, value):
        self.GetProperty().SetDiffuse(value)

    @property
    def diffuse_color(self):
        return self.GetProperty().GetDiffuseColor()

    @diffuse_color.setter
    def diffuse_color(self, value):
        self.GetProperty().SetDiffuseColor(cmap.color(value))

    @property
    def edge_color(self):
        return self.GetProperty().GetEdgeColor()

    @edge_color.setter
    def edge_color(self, value):
        self.GetProperty().SetEdgeColor(cmap.color(value))

    @property
    def edge_visibility(self):
        return self.GetProperty().GetEdgeVisibility()

    @edge_visibility.setter
    def edge_visibility(self, value):
        self.GetProperty().SetEdgeVisibility(value)

    @property
    def lighting(self):
        return self.GetProperty().GetLighting()

    @lighting.setter
    def lighting(self, value):
        self.GetProperty().SetLighting(value)

    @property
    def line_width(self):
        return self.GetProperty().GetLineWidth()

    @line_width.setter
    def line_width(self, value):
        self.GetProperty().SetLineWidth(value)

    @property
    def point_size(self):
        return self.GetProperty().GetPointSize()

    @point_size.setter
    def point_size(self, value):
        self.GetProperty().SetPointSize(value)

    @property
    def render_lines_as_tubes(self):
        return self.GetProperty().GetRenderLinesAsTubes()

    @render_lines_as_tubes.setter
    def render_lines_as_tubes(self, value):
        self.GetProperty().SetRenderLinesAsTubes(value)

    @property
    def render_points_as_spheres(self):
        return self.GetProperty().GetRenderPointsAsSpheres()

    @render_points_as_spheres.setter
    def render_points_as_spheres(self, value):
        self.GetProperty().SetRenderPointsAsSpheres(value)

    @property
    def representation(self):
        rep_mapping = {2: 'surface',
                       1: 'wireframe',
                       0: 'points'}
        return rep_mapping[self.GetProperty().GetRepresentation()]

    @representation.setter
    def representation(self, value):
        rep_mapping = dict(surface=2, points=1, wireframe=0)
        self.GetProperty().SetRepresentation(rep_mapping[value])

    @property
    def specular(self):
        return self.GetProperty().GetSpecular()

    @specular.setter
    def specular(self, value):
        self.GetProperty().SetSpecular(value)

    @property
    def specular_color(self):
        return self.GetProperty().GetSpecularColor()

    @specular_color.setter
    def specular_color(self, value):
        self.GetProperty().SetSpecularColor(cmap.color(value))

    @property
    def specular_power(self):
        return self.GetProperty().GetSpecularPower()

    @specular_power.setter
    def specular_power(self, value):
        self.GetProperty().SetSpecularPower(value)

    @property
    def vertex_color(self):
        return self.GetProperty().GetVertexColor()

    @vertex_color.setter
    def vertex_color(self, value):
        self.GetProperty().SetVertexColor(cmap.color(value))

    @property
    def vertex_visibility(self):
        return self.GetProperty().GetVertexVisibility()

    @vertex_visibility.setter
    def vertex_visibility(self, value):
        self.GetProperty().SetVertexVisibility(value)

    def surface_mode(self):
        self.representation = 'surface'

    def points_mode(self):
        self.representation = 'points'

    def wireframe_mode(self):
        self.representation = 'wireframe'

    @property
    def is_visible(self):
        return bool(self.GetVisibility())

    def hide(self):
        self.SetVisibility(False)

    def show(self):
        self.SetVisibility(True)


class VolActor(vtk.vtkVolume):
    ModalityCT = 'ct'
    ModalityMRI = 'mri'

    TissueBone = 'bone'
    TissueSkin = 'skin'
    TissueMuscles = 'muscles'

    def __init__(self, image, modality='ct', tissue='bone'):
        self._image = image
        self._modality = self._image.modality
        self._tissue = tissue

        self.mapper = vtk.vtkGPUVolumeRayCastMapper()
        self.mapper.SetBlendModeToComposite()
        self.mapper.SetInputData(self.image)
        self.properties = cmap.vmap(modality=self.modality, tissue=self.tissue)
        super().__init__()

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, value):
        if value == self.image:
            return

        self._image = value
        self.mapper.SetInputData(self.image)
        self.Update()

    @property
    def properties(self):
        return self.GetProperty()

    @properties.setter
    def properties(self, value):
        if value == self.properties:
            return
        self.SetProperty(value)

    @property
    def modality(self):
        return self._modality

    @modality.setter
    def modality(self, value):
        if self.modality == value:
            return

        self._modality = value
        self.properties = cmap.vmap(modality=self.modality, tissue=self.tissue)
        self.Update()

    @property
    def tissue(self):
        return self._tissue

    @tissue.setter
    def tissue(self, value):
        if self.tissue == value:
            return

        self._tissue = value
        self.properties = cmap.vmap(modality=self.modality, tissue=self.tissue)
        self.Update()

    @property
    def mapper(self):
        return self.GetMapper()

    @mapper.setter
    def mapper(self, value):
        self.SetMapper(value)

    def bone_mode(self):
        self.tissue = VolActor.TissueBone

    def skin_mode(self):
        self.tissue = VolActor.TissueSkin

    def muscles_mode(self):
        self.tissue = VolActor.TissueMuscles

    def hide(self):
        self.SetVisibility(False)

    def show(self):
        self.SetVisibility(True)

    def pickable_off(self):
        self.PickableOff()

    def pickable_on(self):
        self.PickableOn()
