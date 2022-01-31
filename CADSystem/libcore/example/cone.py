import math
import random

import vtk
import numpy as np

from libcore import Mesh


def normal_extrude(mesh, length=1.0):
    mesh.compute_normals()
    extruder = vtk.vtkLinearExtrusionFilter()
    extruder.SetInputData(mesh)
    extruder.SetExtrusionTypeToNormalExtrusion()
    extruder.SetCapping(True)
    extruder.SetScaleFactor(length)
    extruder.Update()
    return Mesh(extruder.GetOutput())


def make_ribbon(polyline, width=2.0):
    """Делает из линии ленту нулевой толщины и заданной ширины"""
    ribbon_filter = vtk.vtkRibbonFilter()
    ribbon_filter.SetInputData(polyline)
    ribbon_filter.SetWidth(width)
    ribbon_filter.Update()
    result = Mesh(ribbon_filter.GetOutput())
    return result


def to_implicit(mesh):
    imp = vtk.vtkImplicitPolyDataDistance()
    imp.SetInput(mesh)
    return imp


def implicitly_combine(main, to_add_list, to_subtract_list):
    all_meshes = [main]
    all_meshes.extend(to_add_list)
    all_meshes.extend(to_subtract_list)
    all_mesh = Mesh.from_meshes(all_meshes)
    bounding_box = all_mesh.bounds
    del all_mesh

    main_imp = to_implicit(main)
    to_add_imp = [to_implicit(mesh) for mesh in to_add_list]
    to_subtract_imp = [to_implicit(mesh) for mesh in to_subtract_list]

    boolean_sum = vtk.vtkImplicitBoolean()
    boolean_sum.SetOperationTypeToUnion()
    boolean_sum.AddFunction(main_imp)
    for mesh in to_add_imp:
        boolean_sum.AddFunction(mesh)

    boolean_diff = vtk.vtkImplicitBoolean()
    boolean_diff.SetOperationTypeToDifference()
    boolean_diff.AddFunction(boolean_sum)
    for mesh in to_subtract_imp:
        boolean_diff.AddFunction(mesh)

    sampler = vtk.vtkSampleFunction()
    sampler.SetImplicitFunction(boolean_diff)
    sampler.SetModelBounds(bounding_box)
    sampler.SetSampleDimensions(50, 50, 50)

    surface = vtk.vtkContourFilter()
    surface.SetInputConnection(sampler.GetOutputPort())
    surface.SetValue(0, 0.000)
    surface.Update()

    return Mesh(surface.GetOutput())



def mega_tube(pt1, pt2, d1=0.2, d2=0.3, K=0.4):
    NUM_DOTS = 256
    source = vtk.vtkLineSource()
    source.SetPoint1(pt1)
    source.SetPoint2(pt2)
    source.Update()

    spline = vtk.vtkSplineFilter()
    spline.SetInputData(source.GetOutput())
    spline.SetSubdivideToSpecified()
    spline.SetNumberOfSubdivisions(NUM_DOTS)
    spline.Update()

    radii = vtk.vtkDoubleArray()
    radii.SetNumberOfValues(NUM_DOTS+1)
    border = int((1-K)*NUM_DOTS)
    for idx in range(NUM_DOTS+1):
        if idx < border:
            radii.SetValue(idx, d1)
        else:
            x = (idx-border)/(NUM_DOTS-border)
            y = d1 + (d2/d1)*x
            print(x, y)
            radii.SetValue(idx, y)

    mesh = Mesh(spline.GetOutput())
    mesh.GetPointData().SetScalars(radii)
    tube_filter = vtk.vtkTubeFilter()
    tube_filter.SetInputData(mesh)
    tube_filter.SetCapping(True)
    tube_filter.SetRadius(d1)
    tube_filter.SetVaryRadiusToVaryRadiusByScalar()
    tube_filter.SetNumberOfSides(32)
    tube_filter.SetRadiusFactor(d2/d1)


    #tube_filter.SetVaryRadiusToVaryRadiusByScalar()
    #tube_filter.SetVaryRadiusToVaryRadiusByAbsoluteScalar()
    #tube_filter.SetVaryRadius()
    tube_filter.Update()

    return Mesh(tube_filter.GetOutput())

def combine(main, subtract):
    booleanOperation = vtk.vtkBooleanOperationPolyDataFilter()
    # booleanOperation.SetOperationToUnion()
    booleanOperation.SetOperationToIntersection()
    # booleanOperation.SetOperationToDifference()

    booleanOperation.SetInputData(0, main)
    booleanOperation.SetInputData(1, subtract)
    booleanOperation.Update()

    return Mesh(booleanOperation.GetOutput())


if __name__ == '__main__':
    ren = vtk.vtkRenderer()
    ren_win = vtk.vtkRenderWindow()
    ren_win.AddRenderer(ren)

    ren_win.SetSize(1024, 768)

    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(ren_win)

    pt1 = (0.0, 0.0, 0.0)
    pt2 = (0.0, 5.0, 0.0)

    mesh = mega_tube(pt1, pt2, d1=1.1, d2=2.1, K=0.2)
    polyline = Mesh.from_points([(0, 0, -5),
                                 (0, 5, 5)])
    ribbon = normal_extrude(make_ribbon(polyline, width=2.0),
                            length=1.0)
    #ribbon.reconstruct_surface(inplace=True)
    #ribbon.clean(inplace=True)
    #ribbon.close_mesh(inplace=True)

    result = implicitly_combine(main=ribbon,
                                to_subtract_list=[mesh],
                                to_add_list=[])

    # result = combine(main=ribbon,
    #                  subtract=mesh)

    result_mapper = vtk.vtkPolyDataMapper()
    result_mapper.SetInputData(result)
    result_actor = vtk.vtkActor()
    result_actor.SetMapper(result_mapper)
    ren.AddActor(result_actor)

    ribbon_mapper = vtk.vtkPolyDataMapper()
    ribbon_mapper.SetInputData(ribbon)
    ribbon_actor = vtk.vtkActor()
    ribbon_actor.SetMapper(ribbon_mapper)
    #ren.AddActor(ribbon_actor)

    cone_mapper = vtk.vtkPolyDataMapper()
    cone_mapper.SetInputData(mesh)
    cone_actor = vtk.vtkActor()
    cone_actor.SetMapper(cone_mapper)

    #ren.AddActor(cone_actor)




    #--------------------------------------------------
    cubeAxesActor = vtk.vtkCubeAxesActor()
    cubeAxesActor.SetBounds(-5, 5, -5, 5, -5, 5)
    cubeAxesActor.SetCamera(ren.GetActiveCamera())
    cubeAxesActor.GetTitleTextProperty(0).SetColor(1.0, 0.0, 0.0)
    cubeAxesActor.GetLabelTextProperty(0).SetColor(1.0, 0.0, 0.0)
    cubeAxesActor.GetTitleTextProperty(1).SetColor(0.0, 1.0, 0.0)
    cubeAxesActor.GetLabelTextProperty(1).SetColor(0.0, 1.0, 0.0)

    cubeAxesActor.GetTitleTextProperty(2).SetColor(0.0, 0.0, 1.0)
    cubeAxesActor.GetLabelTextProperty(2).SetColor(0.0, 0.0, 1.0)

    cubeAxesActor.DrawXGridlinesOn()
    cubeAxesActor.DrawYGridlinesOn()
    cubeAxesActor.DrawZGridlinesOn()

    cubeAxesActor.XAxisMinorTickVisibilityOff()
    cubeAxesActor.YAxisMinorTickVisibilityOff()
    cubeAxesActor.ZAxisMinorTickVisibilityOff()

    ren.AddActor(cubeAxesActor)
    ren.GetActiveCamera().Azimuth(30)
    ren.GetActiveCamera().Elevation(30)
    ren.ResetCamera()

    iren.Initialize()
    ren_win.Render()
    iren.Start()