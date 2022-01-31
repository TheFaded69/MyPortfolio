import datetime
import os
import re
from collections import UserDict

import h5py
import pydicom


def camel_to_snake(camel_string):
    """ Преобразовать текст из SampleText в sample_text"""
    words_regex = '[A-Z]?[a-z]+|[A-Z]{2,}(?=[A-Z][a-z]|\d|\W|$)|\d+'
    words = re.findall(words_regex, camel_string)
    snake_string = '_'.join(word.lower() for word in words)
    return snake_string


def read_field(fd, name, default=None):
    if name in fd:
        return fd[name].value
    else:
        return default


def write_field(fd, name, value):
    if name in fd:
        del fd[name]
    fd[name] = value
    fd.flush()


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
        # Преобразовать в список и выполнить конвертацию для каждого элемента списка отдельно
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

    # Если переменная строкового типа, то она может содержать число с плавающей точкой. дату или время
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
    return dicom_dict


class MetaData(UserDict):

    @property
    def rows(self):
        return self.data['rows']

    @property
    def columns(self):
        return self.data['columns']

    @property
    def modality(self):
        return self.data['modality']

    @property
    def pixel_spacing(self):
        return self.data['pixel_spacing']

    @property
    def rescale_intercept(self):
        return self.data['rescale_intercept']

    @property
    def rescale_slope(self):
        return self.data['rescale']

    @property
    def slice_thickness(self):
        return self.data['slice_thickness']

    def load_from_hdf(self, fd):
        self.data.clear()

        def add_item(name):
            item_name = name.split('\\')[-1]
            self.data[item_name] = fd[name].value

        fd.visit(add_item)

    def save_to_hdf(self, fd):
        if '/meta' in fd:
            del fd['/meta']

        for key, val in self.items():
            try:
                fd[os.path.join('/meta', key)] = val
            except:
                pass

    @classmethod
    def from_ds(cls, dataset):
        print(dataset)
        as_dict = pydicom_dataset_to_dict(dataset)
        instance = cls()
        instance.update(as_dict)
        return instance

    @classmethod
    def from_file(cls, file_name):
        try:
            ds = pydicom.read_file(file_name, stop_before_pixels=True)
            instance = cls.from_ds(ds)
            return instance
        except:
            return None


if __name__ == '__main__':
    fd = h5py.File('out.h5', 'w')
    ds = pydicom.read_file('../data/dicom/rooster/IM000000', stop_before_pixels=True)
    meta = MetaData.from_ds(ds)
    meta.save_to_hdf(fd)
    meta.load_from_hdf(fd)
    for key, val in meta.items():
        print(key, val)
