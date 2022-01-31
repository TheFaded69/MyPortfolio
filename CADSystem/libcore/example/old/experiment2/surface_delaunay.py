import vtk
import numpy as np
from coco import Mesh
from coco.util import *

mesh = Mesh.sphere()
#mesh.load('../data/fucktopu.stl')
mesh = delaunay_surface(mesh)
print(mesh)
actor = make_actor(mesh)

renderer = vtk.vtkRenderer()
renderer.AddActor(actor)
window = vtk.vtkRenderWindow()
interactor = vtk.vtkRenderWindowInteractor()
window.AddRenderer(renderer)
window.SetSize(1024, 800)
interactor.SetRenderWindow(window)
interactor.Initialize()
interactor.Start()
