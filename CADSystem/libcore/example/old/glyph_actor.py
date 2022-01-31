import vtk

from libcore.mesh import Mesh
from libcore.mixins import ViewportMixin
from libcore.display import PolyActor


class GlyphActor(PolyActor):

    def __init__(self, mesh, glyph, color='green', opacity=1.0, ambient=0.0, ambient_color='white', backface_culling=False,
                 diffuse=1.0, diffuse_color='white', edge_color='black', edge_visibility=False, lighting=True,
                 line_width=1.0, point_size=1.0, render_lines_as_tubes=False, render_points_as_spheres=False,
                 representation='surface', specular=0.0, specular_color='white', specular_power=1.0,
                 vertex_color='peacock', vertex_visibility=False, scalar_visibility=False):

        super().__init__(mesh=mesh,
                         color=color,
                         opacity=opacity,
                         ambient=ambient,
                         ambient_color=ambient_color,
                         backface_culling=backface_culling,
                         diffuse=diffuse,
                         diffuse_color=diffuse_color,
                         edge_color=edge_color,
                         edge_visibility=edge_visibility,
                         lighting=lighting,
                         line_width=line_width,
                         point_size=point_size,
                         render_lines_as_tubes=render_lines_as_tubes,
                         render_points_as_spheres=render_points_as_spheres,
                         representation=representation,
                         specular=specular,
                         specular_color=specular_color,
                         specular_power=specular_power,
                         vertex_color=vertex_color,
                         vertex_visibility=vertex_visibility,
                         scalar_visibility=scalar_visibility)

        self.glyph_mesh = glyph

        glyph = vtk.vtkGlyph3D()
        glyph.SetInputData(self.mesh)
        glyph.SetSourceData(self.glyph_mesh)
        glyph.SetVectorModeToUseNormal()
        glyph.SetScaleModeToScaleByVector()
        glyph.SetScaleFactor(0.25)
        glyph.Update()

        self.mapper.SetInputData(glyph.GetOutput())
        self.actor.SetMapper(self.mapper)

class App(ViewportMixin):

    def __init__(self):
        super().__init__()

        original = Mesh('../data/rooster.midres.stl')
        original.compute_normals()
        arrow = Mesh.arrow()
        normals = GlyphActor(mesh=original.mask_on_ratio(ratio=8),
                             glyph=arrow)
        self.add_prop(PolyActor(mesh=original, color='white'))
        self.add_prop(normals)

if __name__ == '__main__':
    app = App()
    app.run()
