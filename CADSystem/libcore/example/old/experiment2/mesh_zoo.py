import vtk
import numpy as np
from coco import Mesh
from coco.util import *

from glob import glob

files = glob('../data/*.stl')
for file in files:
    data = Mesh()
    data.load(file)
    show([dict(polydata=data)])