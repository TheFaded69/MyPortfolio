"""Цвета, цветовые карты, волюметрирический мэппинг

Данные хрянятся в .yml файлах внутри папки data/ пакета **libcore**.
"""
import random
from collections import namedtuple

import numpy as np
import vtk
import yaml

from .utils import res_filename

__all__ = ['Color', 'CMap', 'VMap',
           'colors', 'color', 'random_color',
           'cmaps', 'cmap', 'cmap_thumb',
           'vmaps', 'vmap']

Color = namedtuple('Color', ['r', 'g', 'b'])
Color.__doc__ = "Цвет в представлении r, g, b"

CMap = namedtuple('CMap', ['name', 'colors'])
CMap.__doc__ = "Цветовая карта, список входящих в нее цветов"

VMap = namedtuple('VMap',
                  ['modality', 'tissue', 'color', 'scalar_opacity', 'gradient_opacity', 'ambient', 'diffuse',
                   'specular'])
VMap.__doc__ = "Параметры волюметрического рендеринга"


def colors(name_only=True):
    """Перечисление доступных цветов.

    :param name_only: возращать только имена цветов, по умолчанию: True
    :return color_name или color_name, Color
    """
    if name_only:
        for color_name in _COLORS.keys():
            yield color_name
    else:
        for color_name, val in _COLORS.items():
            yield color_name, val


def color(color, uint8=False):
    """Цвет.

    :param color: имя цвета или последовательность с тремя значениями
    :param uint8: если истина - используются значения компонент цвета `0..255`
    :return Color
    """
    if isinstance(color, str):
        rgb = _COLORS[color]
    else:
        rgb = Color(*color)

    if uint8:
        rgb = Color(r=int(rgb.r * 255),
                    g=int(rgb.g * 255),
                    b=int(rgb.b * 255))
    return rgb


def random_color(uint8=False):
    """Случайный цвет.

    :param uint8: если истина - используются значения компонент цвета `0..255`
    :return Color
    """
    color_name = random.choice(list(colors()))
    return color(color_name, uint8=uint8)


def cmaps(name_only=True):
    """Доступные цветовые карты.

    :param name_only: возращать только имена, по умолчанию: True
    :return cmap_name или cmap_name, CMap

    """
    if name_only:
        for cmap_name in _CMAPS.keys():
            yield cmap_name
    else:
        for cmap_name, val in _CMAPS.items():
            yield cmap_name, val


def cmap(mapping, num_colors=256, min_value=-2048, max_value=2048):
    """ LUT для цветовой карты. Используется интерполяция для получения lut в заданном диапазоне,
    с заданным числом цветов.

    :param mapping: цветовая карта или ее название
    :param num_colors: количество элементов в создаваемой lut
    :param min_value: начальное значение диапазона
    :param max_value: конечное значение диапазона
    :return vtk.vtkLookupTable
    """
    if isinstance(mapping, str):
        cm = _CMAPS[mapping]
        colors = cm.colors
    elif isinstance(mapping, CMap):
        colors = mapping.colors
    else:
        colors = list(mapping)

    # Функция передачи цвета.
    ctf = vtk.vtkColorTransferFunction()
    ctf.SetColorSpaceToDiverging()
    ctf.SetRange(min_value, max_value)
    ctf_scalar_values = list(np.linspace(min_value, max_value, len(colors)))
    # Добавляем цвета из определения цветовой карты
    for val, color in zip(ctf_scalar_values, colors):
        ctf.AddRGBPoint(val, color[0], color[1], color[2])

    # Интерполированные цвета
    colors_interpolated = list()
    color = [0.0, 0.0, 0.0]
    for idx, val in enumerate(np.linspace(min_value, max_value, num_colors)):
        ctf.GetColor(val, color)
        colors_interpolated.append(tuple(color))

    # Конструируем LUT
    lut = vtk.vtkLookupTable()
    lut.SetNumberOfTableValues(num_colors)
    lut.SetTableRange(min_value, max_value)
    lut.Build()

    # Наполняем интерполированными цветами
    for idx, color in enumerate(colors_interpolated):
        if len(color) == 3:
            color = tuple(color) + (1.0,)
        lut.SetTableValue(idx, color)
    return lut


def cmap_thumb(mapping, width=64, height=64):
    """Демонстрационное изображение для цветовой карты.

    :param mapping: цветовая карта (vtk.vtkLookupTable)
    :param width: ширина изображения
    :param height: высота изображения
    :return изображение, демонстрирующее цветовую карту
    """
    min_value, max_value = mapping.GetTableRange()
    clr = [0.0, 0.0, 0.0]
    image = np.zeros((height, width, 3), dtype=np.uint8)

    for idx, val in enumerate(np.linspace(min_value, max_value, width)):
        mapping.GetColor(val, clr)
        image[:, idx] = color(clr, uint8=True)

    return image


def vmaps():
    """Доступные волюметрические отображения"""
    # TODO: Сделать более читаемым
    for modality in _VMAPS.values():
        for tissue in modality.values():
            yield tissue


def vmap(modality, tissue):
    """Пресет для волюметрического рендеринга"""
    props = _VMAPS[modality][tissue]
    color_func = vtk.vtkColorTransferFunction()
    for pt in props.color:
        color_func.AddRGBPoint(*pt)

    scalar_opacity_func = vtk.vtkPiecewiseFunction()
    for pt in props.scalar_opacity:
        scalar_opacity_func.AddPoint(*pt)

    gradient_opacity_func = vtk.vtkPiecewiseFunction()
    for pt in props.gradient_opacity:
        gradient_opacity_func.AddPoint(*pt)

    volume_property = vtk.vtkVolumeProperty()
    volume_property.SetColor(color_func)
    volume_property.SetScalarOpacity(scalar_opacity_func)
    volume_property.SetGradientOpacity(gradient_opacity_func)
    volume_property.SetInterpolationTypeToLinear()
    volume_property.ShadeOn()
    volume_property.SetAmbient(props.ambient)
    volume_property.SetDiffuse(props.diffuse)
    volume_property.SetSpecular(props.specular)

    return volume_property


def _load_colors():
    file_name = res_filename(_COLORS_DATA_FILE_NAME)
    colors = dict()
    with open(file_name, 'r') as f:
        data = yaml.load(f)
        colors = {name: Color(*color) for name, color in data.items()}
    return colors


def _load_mappings():
    file_name = res_filename(_MAPPINGS_DATA_FILE_NAME)
    mappings = dict()
    with open(file_name, 'r') as f:
        data = yaml.load(f)
        for name, val in data.items():
            mappings[name] = CMap(name=val['name'],
                                  colors=[Color(*color) for color in val['colors']])
    return mappings


def _load_volume_mappings():
    file_name = res_filename(_VOLUME_DATA_FILE_NAME)
    mappings = dict(ct=dict(), mri=dict())
    with open(file_name, 'r') as f:
        data = yaml.load(f)
        for modality in ['ct', 'mri']:
            for tissue, value in data[modality].items():
                mapping = VMap(**value)
                mappings[modality][tissue] = mapping

    return mappings


_COLORS_DATA_FILE_NAME = 'data/colors.yml'
_MAPPINGS_DATA_FILE_NAME = 'data/colormaps.yml'
_VOLUME_DATA_FILE_NAME = 'data/volume.yml'
_COLORS = _load_colors()
_CMAPS = _load_mappings()
_VMAPS = _load_volume_mappings()
