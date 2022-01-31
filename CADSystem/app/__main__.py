import os
import sys
import datetime

from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtGui

from .controllers.projectdialog import ProjectDialog

from . import resources_rc


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    path = getattr(sys, '_MEIPASS', os.getcwd())
    # path2 = os.path.abspath('.') + '/'
    os.chdir(path)
    paths = QCoreApplication.libraryPaths()
    paths.append(".")
    paths.append("PyQt5/Qt/plugins")
    QCoreApplication.setLibraryPaths(paths)

    from .controllers.mainwindow import MainWindow
    mw = MainWindow()
    mw.showMaximized()

    today = datetime.datetime.today()
    log = open('C:/Users/Public/Documents/log_file.txt', 'a')
    log.write('Начало работы: ' + today.strftime("%d-%m-%Y %H.%M.%S") + '\n')
    log.close()

    # mw.showFullScreen

    # from .models.image import imageModel
    # from .models.editor import editorModel
    # from .models.implantor import implantorModel
    # from .models.mirrorer import mirrorerModel

    # from libcore.display import PolyActor

    # implantorModel.addProp('implant', PolyActor(Mesh('./implant.midres.stl')))
    # editorModel.addProp('mesh', PolyActor(Mesh('./pet_1.stl')))
    # editorModel.addProp('implant', PolyActor(Mesh('./pet_2.stl')))
    # editorModel.addProp('left', PolyActor(Mesh('./pet_3.stl')))
    # implantorModel.addProp('mesh', PolyActor(Mesh('./pet_1.stl')))
    # implantorModel.addProp('left', PolyActor(Mesh('./pet_3.stl')))
    # mirrorerModel.mesh = Mesh('./pet_1.stl')
    # mounterModel.mesh = Mesh('./123.stl')
    # mounterModel.implant = Mesh('./123.stl')

    # import pydicom
    # import numpy as np

    # from libcore.image import Image
    # from libcore.dicom import read_metadata

    # print(path2)
    # import configparser
    # config = configparser.ConfigParser()
    # config.read(path2 + 'config.ini')
    # CADSI_DICOM = path2 + config.get('CADSI', 'dicom')
    # CADSI_SPACING = list(map(float, config.get('CADSI', 'spacing').split(',')))

    # ds = pydicom.dcmread(CADSI_DICOM)
    # meta_data = read_metadata(CADSI_DICOM)

    # rows = meta_data['rows']
    # columns = meta_data['columns']
    # slices = meta_data['total_frames']
    # data = np.zeros((rows, columns, slices), dtype=np.int16)

    # for idx, slice_data in enumerate(ds.pixel_array):
    #     data[:, :, idx] = slice_data

    # volume = data.transpose(2, 0, 1)

    # if 'slice_thickness' in meta_data:
    #     spacings = [meta_data['pixel_spacing'][0],
    #                 meta_data['pixel_spacing'][1],
    #                 meta_data['slice_thickness']]
    # if 'reconstruction_interval' in meta_data:
    #     spacings = [meta_data['pixel_spacing'][0],
    #                 meta_data['pixel_spacing'][1],
    #                 float(meta_data['reconstruction_interval'])]
    # if 'spacing_between_slices' in meta_data:
    #     spacings = [meta_data['pixel_spacing'][0],
    #                 meta_data['pixel_spacing'][1],
    #                 float(meta_data['spacing_between_slices'])]
    # if min_location != max_location:
    #     spacings = [meta_data['pixel_spacing'][0],
    #                 meta_data['pixel_spacing'][1],
    # float(abs(max_location - min_location) / meta_data['total_frames'])]

    # image = Image.from_numpy(volume,
    #                          spacing=CADSI_SPACING,
    #                          origin=(0, 0, 0),
    #                          modality='ct')

    # image.shift_scale(scale=meta_data['rescale_slope'],
    #                   shift=meta_data['rescale_intercept'],
    #                   inplace=True)

    # imageModel.setImage(image)

    # #########################################################3

    # from .models.stage import stageModel
    # from .models.mounter import mounterModel
    # from libcore.mesh import Mesh

    # mounterModel.mesh = Mesh('./pet_1.stl')
    # mounterModel.implant = Mesh('./pet_2.stl')
    # stageModel.stage = 6

    # #########################################################3

    # from .models.stage import stageModel
    # from .models.editor import editorModel
    # from libcore.mesh import Mesh
    # from libcore.display import PolyActor

    # editorModel.addProp('mesh', PolyActor(Mesh('./pet_1.stl')))
    # editorModel.addProp('implant', PolyActor(Mesh('./pet_2.stl')))
    # stageModel.stage = 3
    sys.exit(app.exec())




if __name__ == "__main__":
    main()
