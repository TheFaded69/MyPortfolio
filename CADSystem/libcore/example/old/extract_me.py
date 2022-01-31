import vtk
from libcore.mixins import ViewportMixin
from libcore.image import Image
from libcore.widget import ImageView
from libcore import dicom

class App(ViewportMixin):

    def __init__(self):
        super().__init__()
        self.style = vtk.vtkInteractorStyleTrackballCamera()
        self.register_callback(vtk.vtkCommand.CharEvent, self.event)

        self.image = Image()
        self.image.load('../../data/rooster.vti')
        self.image.clip_values(inplace=True)

        thresholder = vtk.vtkImageThreshold()
        thresholder.SetInputData(self.image)
        thresholder.ThresholdBetween(400, 1200)
        thresholder.ReplaceInOn()
        thresholder.SetInValue(0)
        thresholder.ReplaceOutOn()
        thresholder.SetOutValue(1)
        thresholder.Update()
        self.image = Image(thresholder.GetOutput())

        self.image_view = ImageView(self.interactor, self.image)
        self.image_view.show()


        #self.image.median3d(kernel_size=(7, 7, 7), inplace=True)
        # print('Median filtering...')
        # selimage.median3d(kernel_size=(7, 7, 7), inplace=True)
        # print('Anysotropic filtering...')
        # self.image.denoise(factor=5.0, threshold=10.0, inplace=True)
        # print('Extracting surface...')
        # self.mesh = self.image.extract_surface(threshold=250,
        #                                        discrete=True)
        #
        # thresholder = vtk.vtkImageThreshold()
        # thresholder.SetInputData(self.image)
        # thresholder.ThresholdBetween(400, 1200)
        # thresholder.ReplaceInOn()
        # thresholder.SetInValue(0)
        # thresholder.ReplaceOutOn()
        # thresholder.SetOutValue(1)
        # thresholder.Update()
        # show_image(thresholder.GetOutput(), axis=0)
        #
        # extractor = vtk.vtkDiscreteMarchingCubes()
        # extractor.ComputeGradientsOn()
        # extractor.ComputeNormalsOn()
        # extractor.ComputeScalarsOff()
        # extractor.SetInputData(thresholder.GetOutput())
        # extractor.GenerateValues(1, 1, 1)

        # self.add_prop(PolyActor(self.mesh, color='blue', ambient=0.0, specular_power=1.0))
        # self.edges = self.mesh.extract_edges().split()
        #
        # for edge in self.edges:
        #     self.add_prop(PolyActor(edge, edge_visibility=True, line_width=2.5, edge_color=random_color()))

    def event(self, caller, ev):
        key = self.interactor.GetKeySym()
        if key == 'a':
            print('a is pressed')
        self.rwindow.Render()

app = App()
app.run()
