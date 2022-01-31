import datetime
from collections import namedtuple

import numpy as np
import pydicom

from .image import Image
from .utils import camel_to_snake
from .utils import walk_dir

__all__ = ["read_metadata",
           "scan_directory",
           "read_slice",
           "read_volume",
           "load_directory"]


def read_metadata(file_name):
    """ Чтение метаданных .dicom-файла

        Если файл не является .dicom-файлов - возвращаем None
    """
    try:
        ds = pydicom.read_file(file_name, stop_before_pixels=True)
    except ValueError:
        return None
    except Exception:
        return None

    # print(ds)
    return pydicom_dataset_to_dict(ds)


def scan_directory(dir_name):
    """ Просканировать дирректорию на наличие dicom-серий

        На выходе словарь. Ключи: полные имена файлов, Значения: метаинформация для файла.
    """
    # Получаем iterable по файлам из папки
    walker = walk_dir(dir_name)
    # Класс для хранения пар имя файла: метаинфо
    pair = namedtuple('pair', ['file_name', 'meta_info'])
    # processes на самом деле - количество нитей

    # with thread.Pool(processes=8) as pool:
    #     # Параллельный итератор по парам имяфайла: метаинформация
    #     it = pool.imap_unordered(lambda fn: pair(fn, read_metadata(fn)), walker)
    #     # Если файл не удалось загрузить, то pair.meta_info будет равно None
    #     discovered = {pair.file_name: pair.meta_info for pair in it
    #                   if pair.meta_info}
    discovered = dict()
    for filename in walker:
        metadata = read_metadata(filename)
        if metadata:
            discovered[filename] = metadata
    return discovered


def read_slice(file_name):
    """ Загрузка одиночного .dicom файла в виде numpy-массива """
    ds = pydicom.read_file(file_name)
    return ds.pixel_array


def read_volume(files):
    meta_data = read_metadata(files[0])

    modality = 'ct'
    if 'modality' in meta_data.keys():
        modality = meta_data['modality'].lower()
    print('Modality: {}'.format(modality))

    all_meta_datas = [read_metadata(fname) for fname in files]
    slice_locations = [md['slice_location'] for md in all_meta_datas]
    min_location = min(slice_locations)
    max_location = max(slice_locations)

    rows = meta_data['rows']
    columns = meta_data['columns']
    slices = len(files)
    data = np.zeros((rows, columns, slices), dtype=np.int16)

    for idx, file_name in enumerate(files):
        slice_data = read_slice(file_name)
        data[:, :, idx] = slice_data

    # pool = mp.Pool()
    # for idx, slice_data in enumerate(pool.imap(read_slice, files)):
    #     print('data', data.shape)
    #     print('slice_data', slice_data.shape)
    #     data[:, :, idx] = slice_data
    # pool.close()
    # pool.join()
    volume = data.transpose(2, 0, 1)


    if 'slice_thickness' in meta_data:
        spacings = [meta_data['pixel_spacing'][0],
                    meta_data['pixel_spacing'][1],
                    meta_data['slice_thickness']]
    if 'reconstruction_interval' in meta_data:
        spacings = [meta_data['pixel_spacing'][0],
                    meta_data['pixel_spacing'][1],
                    float(meta_data['reconstruction_interval'])]
    if 'spacing_between_slices' in meta_data:
        spacings = [meta_data['pixel_spacing'][0],
                    meta_data['pixel_spacing'][1],
                    float(meta_data['spacing_between_slices'])]
    if min_location != max_location:
        spacings = [meta_data['pixel_spacing'][0],
                    meta_data['pixel_spacing'][1],
                    float(abs(max_location - min_location) / len(files))]

    # for key, val in meta_data.items():
    #    print(key, val)

    # print(meta_data['reconstruction_interval'])

    image = Image.from_numpy(volume, spacing=spacings, origin=(0, 0, 0), modality=modality)
    for n, v in meta_data.items():
        print(n, ' : ', v)

    if modality == 'ct':
        image.shift_scale(scale=meta_data['rescale_slope'],
                          shift=meta_data['rescale_intercept'],
                          inplace=True)

    return image


def sort_files(files):
    # TODO: Вынести отдельно код для сортировки
    location_filename_pairs = list()
    for fname in files:
        meta_data = read_metadata(fname)
        if 'slice_location' not in meta_data:
            continue
        pair = tuple((meta_data['slice_location'], fname))
        location_filename_pairs.append(pair)
    files = [fname for location, fname in sorted(location_filename_pairs)]
    return files


def load_directory(dir_name):
    discovered = scan_directory(dir_name)
    location_filename_pairs = list()
    for fname, info in discovered.items():
        if 'slice_location' not in info:
            continue
        pair = tuple((info['slice_location'], fname))
        location_filename_pairs.append(pair)
    files = [fname for location, fname in sorted(location_filename_pairs)]
    return read_volume(files)


def pydicom_type_to_python(value):
    """Преобразование типов из специфических для pydicom к встроенным"""

    if hasattr(value, 'decode'):
        try:
            value = value.decode(encoding='utf-8')
        except Exception:
            pass

    # Списки, целые числа и числа с плавающей точкой оставляем без изменений
    if type(value) in [list, int, float]:
        return value

    # Отображение тип -> функция преобразования, для типов из pydicom
    mapping_table = {
        pydicom.valuerep.DA: datetime.datetime.date,
        pydicom.valuerep.DT: datetime.datetime,
        pydicom.valuerep.TM: datetime.datetime.time,
        pydicom.valuerep.DSfloat: float,
        pydicom.valuerep.PersonName3: str,
        pydicom.valuerep.IS: int,
        pydicom.dataset.Dataset: pydicom_dataset_to_dict,
        # Преобразовать в список и выполнить конвертацию для каждого элемента
        # списка отдельно
        pydicom.multival.MultiValue: lambda x: [pydicom_type_to_python(v) for v in list(x)],
        pydicom.uid.UID: str,
    }

    # Если тип из pydicom
    # Пробуем выполнить преобразование согласно отображению
    value_type = type(value)
    if value_type in mapping_table:
        try:
            mapping = mapping_table[value_type]
            return mapping(value)
        except (TypeError, ValueError):
            pass

    # Если переменная строкового типа, то она может содержать число с
    # плавающей точкой. дату или время
    if isinstance(value, str):
        try:
            return float(value)
        except (TypeError, ValueError):
            pass

        try:
            return datetime.datetime.strptime(value, "%Y%m%d")
        except ValueError as e:
            pass

        try:
            dt = datetime.datetime.strptime(value, "%H%M%S.%f")
            return dt.time()
        except ValueError as e:
            pass

    return str(value).strip()


def pydicom_dataset_to_dict(dataset):
    """ Преобразование pydicom dataset в словарь

        Имена преобразуются согласно pep8.
        Значения конвертируются из pydicom формата во встроенные типы питона.
        Наличие конкретных ключей зависит от .dicom файла.
    """
    dicom_dict = dict()
    # Для каждого элемента в датасете
    for elem in dataset:
        # Создаем имя-ключ
        if elem.keyword:
            key_name = camel_to_snake(elem.keyword)
        else:
            key_name = camel_to_snake(elem.name)
        # Игнорировать пустые
        if not key_name:
            continue
        # Преобразуем элемент
        dicom_dict[key_name] = pydicom_type_to_python(elem.value)

    # (01f1, 1032) Private tag data                    CS: 'RIGHTONLEFT'
    if dataset.get((0x01f1, 0x1032)):
        dicom_dict['rightonleft'] = True
    else:
        dicom_dict['rightonleft'] = False

    return dicom_dict
