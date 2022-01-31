from typing import Iterable

import vtk

from .mesh import Mesh
from .geometry import point_distance
from .geometry import vec_cross, vec_normalize, vec_norm, vec_dot, vec_subtract

def extract_cells_using_points(mesh, points):
    ids = vtk.vtkIdTypeArray()
    ids.SetNumberOfComponents(1)

    # Set values
    for i in points:
        ids.InsertNextValue(i)

    selectionNode = vtk.vtkSelectionNode()
    selectionNode.SetFieldType(vtk.vtkSelectionNode.POINT)
    selectionNode.SetContentType(vtk.vtkSelectionNode.INDICES)
    selectionNode.SetSelectionList(ids)
    selectionNode.GetProperties().Set(vtk.vtkSelectionNode.CONTAINING_CELLS(), 1)

    selection = vtk.vtkSelection()
    selection.AddNode(selectionNode)

    extractSelection = vtk.vtkExtractSelection()

    extractSelection.SetInputData(0, mesh)
    extractSelection.SetInputData(1, selection)
    #extractSelection.Update()

    sf = vtk.vtkDataSetSurfaceFilter()
    sf.SetInputConnection(extractSelection.GetOutputPort())
    sf.Update()

    return Mesh(sf.GetOutput())
    #
    # # In selection
    # selected = vtk.vtkUnstructuredGrid()
    # selected.ShallowCopy(extractSelection.GetOutput())
    #
    # print("There are {} point in the selection".format(selected.GetNumberOfPoints()))
    # print("There are {} cells in the selection".format(selected.GetNumberOfCells()))
    #
    # # Get points that are NOT in the selection
    # selectionNode.GetProperties().Set(vtk.vtkSelectionNode.INVERSE(), 1)  # invert the selection
    # extractSelection.Update()
    #
    # notSelected = vtk.vtkUnstructuredGrid()
    # notSelected.ShallowCopy(extractSelection.GetOutput())
    #
    # print("There are {} points NOT in the selection.".format(notSelected.GetNumberOfPoints()))
    # print("There are {} cells NOT in the selection.".format(notSelected.GetNumberOfCells()))


def closest_point_idx(mesh, coord, n=1):
    locator = vtk.vtkPointLocator()
    locator.SetDataSet(mesh)
    locator.BuildLocator()
    if n == 1:
        point_idx = locator.FindClosestPoint(coord)
    else:
        point_ids = vtk.vtkIdList()
        locator.FindClosestNPoints(n, coord, point_ids)
        point_idx = ids_to_list(point_ids)
    return point_idx


def points_ids_within_radius(mesh, coord, radius=0.1):
    locator = vtk.vtkPointLocator()
    locator.SetDataSet(mesh)
    locator.BuildLocator()
    points_ids = vtk.vtkIdList()
    locator.FindPointsWithinRadius(radius, coord, points_ids)
    return ids_to_list(points_ids)


def delete_cells(mesh, indexes):
    mesh.BuildLinks()
    if isinstance(indexes, vtk.vtkIdList):
        indexes = ids_to_list(indexes)
    else:
        indexes = list(indexes)

    for idx in indexes:
        mesh.DeleteCell(idx)
    mesh.RemoveDeletedCells()
    mesh.Modified()


def points_for_face(mesh, index):
    ids = vtk.vtkIdList()
    mesh.GetCellPoints(index, ids)
    return ids_to_list(ids)


def face_for_point(mesh, index):
    ids = vtk.vtkIdList()
    mesh.GetPointCells(index, ids)
    return ids_to_list(ids)


def cell_neighbors(mesh, index):
    """Возвращает индексы ячеек соседних с ячейкой cell_id"""
    neighbours = list()
    points = points_for_face(mesh, index)
    for point in points:
        neighbours.extend(face_for_point(mesh, point))
    return list(set(neighbours))


def find_geodesic(mesh, start, end):
    dijkstra = vtk.vtkDijkstraGraphGeodesicPath()
    dijkstra.SetInputData(mesh)
    dijkstra.SetStartVertex(start)
    dijkstra.SetEndVertex(end)
    dijkstra.Update()
    return Mesh(dijkstra.GetOutput())


def extract_cells(mesh, indexes):
    cellids = list_to_ids(indexes)
    extract = vtk.vtkExtractCells()  # extract cells with specified cellids
    extract.SetInputData(mesh)
    extract.AddCellList(cellids)
    extract.Update()
    extraction = extract.GetOutput()
    geometry = vtk.vtkGeometryFilter()  # unstructured grid to polydata
    geometry.SetInputData(extraction)
    geometry.Update()
    return geometry.GetOutput()


def dilate_selection(mesh, selection):
    new_selection = list(selection)
    for cellid in selection:
        new_selection.extend(cell_neighbors(mesh, cellid))
    new_selection = list(set(new_selection))
    return new_selection


def delaunay_surface(mesh):
    points = vtk.vtkPoints()
    points.DeepCopy(mesh.GetPoints())
    profile = vtk.vtkPolyData()
    profile.SetPoints(points)
    delny = vtk.vtkDelaunay3D()
    delny.SetInputData(profile)
    delny.SetTolerance(0.001)
    delny.Update()
    surface = vtk.vtkDataSetSurfaceFilter()
    surface.SetInputData(delny.GetOutput())
    surface.Update()
    return surface.GetOutput()


def ids_to_list(ids):
    if isinstance(ids, vtk.vtkIdList):
        ids_list = [ids.GetId(i) for i in range(ids.GetNumberOfIds())]
    elif isinstance(ids, Iterable):
        ids_list = list(ids)
    else:
        ids_list = [ids]
    return ids_list


def list_to_ids(ids_list):
    vtk_ids = vtk.vtkIdList()
    for id in ids_list:
        vtk_ids.InsertNextId(id)
    return vtk_ids

def mesh_inflate(mesh, center, radius):
    points = mesh.points
    if mesh.normals is None:
        mesh.compute_normals()
    normals = mesh.normals

    warp_vectors = [list([0.0, 0.0, 0.0]) for idx in range(mesh.number_of_points)]
    enclosed_indexes = points_ids_within_radius(mesh=mesh, coord=center, radius=radius)
    for idx in enclosed_indexes:
        point = points[idx]
        normal = normals[idx]

        print('center: {} \t\t idx: {}\t\tpt: {}\t\tnorm: {}\t\t {}'.format(center, idx, point, normal, vec_norm(normal)))

        distance = point_distance(point, center)
        direction = vec_subtract(center, point)
        vec = [distance*n for n in vec_normalize(vec_cross(normal, direction))]
        warp_vectors[idx] = list(direction)

    mesh.warp(vecs=warp_vectors, inplace=True)
    return mesh


def mesh_deflate(mesh, center, radius):
    points = mesh.points
    if mesh.normals is None:
        mesh.compute_normals()
    normals = mesh.normals

    warp_vectors = [[0.0, 0.0, 0.0] for idx in range(mesh.number_of_points)]
    enclosed_indexes = points_ids_within_radius(mesh=mesh, coord=center, radius=radius)
    for idx in enclosed_indexes:
        point = points[idx]
        normal = normals[idx]

        distance = point_distance(point, center)
        direction = vec_subtract(point, center)
        vec = [distance*radius*n for n in direction]
        warp_vectors[idx] = list(direction)

    mesh.warp(vecs=warp_vectors, inplace=True)
    return mesh
