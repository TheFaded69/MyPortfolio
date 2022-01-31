import h5py
from libcore.image import Image
from libcore.metadata import MetaData
from libcore.patient import Patient


class State(object):
    def __init__(self):
        self.patient = Patient()
        self.metadata = MetaData()
        self.image = Image()
        self.models = list()
        self.implants = list()

    def load(self, filename):
        fd = h5py.File(filename, 'r')
        self.patient.load_from_hdf(fd)
        self.metadata.load_from_hdf(fd)

    def save(self, filename):
        pass


if __name__ == '__main__':
    pass
