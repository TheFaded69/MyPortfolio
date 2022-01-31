import cv2
import time
import vtk

from libcore.image import Image
from libcore.image import vtkimage_to_numpy
from libcore.display import VolActor

def make_preview(image, width=512, height=512):
    actor = VolActor(image)
    renderer = vtk.vtkRenderer()
    renderer.AddActor(actor)
    render_window = vtk.vtkRenderWindow()
    render_window.SetOffScreenRendering(1)
    render_window.AddRenderer(renderer)
    render_window.SetSize(width, height)

    camera = renderer.GetActiveCamera()
    camera.SetPosition(0, -1.0, 0)
    camera.SetFocalPoint(0, 0.0, 0)
    renderer.ResetCamera()
    camera.Zoom(1.5)
    camera.Roll(180)

    render_window.Render()

    window_to_image_filter = vtk.vtkWindowToImageFilter()
    window_to_image_filter.SetInput(render_window)
    window_to_image_filter.Update()

    result = Image(window_to_image_filter.GetOutput())
    as_numpy = vtkimage_to_numpy(result)
    #as_numpy = as_numpy[:, :, [2, 1, 0]]
    return as_numpy

# def numpy2pixmap(image):
#     height, width, channel = image.shape
#     bytesPerLine = 3 * width
#     qImg = QImage(cvImg.data, width, height, bytesPerLine, QImage.Format_RGB888)
#     return QtGui.QPixmap(image)


if __name__ == '__main__':
    image = Image('../data/rooster.vti')

    start = time.process_time()
    offline = make_preview(image)
    end = time.process_time()
    print(end - start)

    cv2.imshow('image', offline)
    cv2.waitKey(0)
