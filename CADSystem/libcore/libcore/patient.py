"""

"""

import os

import h5py
import imageio


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


class Patient(object):

    def __init__(self,
                 name='',
                 sex='',
                 date_of_birth='',
                 weight=0.0,
                 photo=None):

        self.name = name
        self.sex = sex
        self.date_of_birth = date_of_birth
        self.weight = weight
        self.photo = photo

    def load_from_hdf(self, fd):
        self.name = read_field(fd, '/patient/name', default='')
        self.sex = read_field(fd, '/patient/sex', default='')
        self.date_of_birth = read_field(fd, '/patient/date_of_birth', default='')
        self.weight = read_field(fd, '/patient/weight', default=0.0)
        self.photo = read_field(fd, '/patient/photo', default=None)

    def save_to_hdf(self, fd):
        write_field(fd, '/patient/name', self.name)
        write_field(fd, '/patient/sex', self.sex)
        write_field(fd, '/patient/date_of_birth', self.date_of_birth)
        write_field(fd, '/patient/weight', self.weight)
        if self.photo is not None:
            write_field(fd, '/patient/photo', self.photo)

    def load_photo(self, file_name):
        if os.path.exists(file_name):
            self.photo = imageio.imread(file_name)

    @property
    def age(self):
        return 0

    def __repr__(self):
        fmt = 'Patient(name="{}", sex="{}", date_of_birth="{}", weight="{}")'
        return fmt.format(self.name, self.sex, self.date_of_birth, self.weight)


if __name__ == '__main__':
    fd = h5py.File('out.h5', 'w')

    patient = Patient()
    patient.weight = 100.0
    patient.name = 'Петухова'
    patient.sex = 'F'
    patient.load_photo('photo.jpg')
    patient.save_to_hdf(fd)

    del patient

    patient = Patient()
    patient.load_from_hdf(fd)

    print(patient)
