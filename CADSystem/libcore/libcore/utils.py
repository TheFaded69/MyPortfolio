import os
import re
import time
from contextlib import contextmanager
import tempfile

import pkg_resources
import vtk
from libcore.display import VolActor

from .image import Image

__all__ = ['link_to_file',
           'camel_to_snake',
           'walk_dir',
           'timeit']


def link_to_file(file_name):
    tmp_file = tempfile.gettempdir() + '/vtktmpfile.lnk'
    if not os.path.exists(file_name):
        open(file_name, 'w').close()
    if os.path.exists(tmp_file):
        os.remove(tmp_file)
    os.link(file_name, tmp_file)
    return tmp_file


def camel_to_snake(camel_string):
    """ Преобразовать текст из SampleText в sample_text"""
    words_regex = '[A-Z]?[a-z]+|[A-Z]{2,}(?=[A-Z][a-z]|\d|\W|$)|\d+'
    words = re.findall(words_regex, camel_string)
    snake_string = '_'.join(word.lower() for word in words)
    return snake_string


def walk_dir(dir_name):
    """ Генератор, по очереди возвращает файлы из папки и ее подпапок """
    for (path, dirs, files) in os.walk(dir_name):
        for file in files:
            yield os.path.join(path, file)


@contextmanager
def timeit(msg):
    print(msg, '...', )
    start = time.clock()
    try:
        yield
    finally:
        print("%.2f ms" % ((time.clock() - start) * 1000))


def load_resource(name):
    file_name = pkg_resources.resource_filename("libcore", name)
    fname, ext = os.path.splitext(file_name)
    return file_name


def res_filename(name):
    return pkg_resources.resource_filename("libcore", name)


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
    return result.as_numpy()
