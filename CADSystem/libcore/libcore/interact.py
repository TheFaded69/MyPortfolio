import vtk


from .geometry import point_distance
from .geometry import vec_normalize
from .mesh import Mesh
from .topology import find_geodesic
from .display import PolyActor

class StyleActorSelection(vtk.vtkInteractorStyleTrackballCamera):
    def __init__(self, on_click=None):
        self.on_click = on_click
        self.picker = vtk.vtkPropPicker()

        self.AddObserver("LeftButtonPressEvent", self.event)
        self.AddObserver("RightButtonPressEvent", self.event)
        self.AddObserver("MiddleButtonPressEvent", self.event)

    @property
    def interactor(self):
        return self.GetInteractor()

    @property
    def renderer(self):
        return self.interactor.GetRenderWindow().GetRenderers().GetFirstRenderer()


    def event(self, obj, event):
        x, y = self.GetInteractor().GetEventPosition()
        self.picker.Pick(x, y, 0, self.renderer)
        pick = self.picker.GetActor()

        if pick and self.on_click:
            if event == "LeftButtonPressEvent":
                self.OnLeftButtonDown()
                button = 'left'
            elif event == "RightButtonPressEvent":
                self.OnRightButtonDown()
                button = 'right'
            elif event == "MiddleButtonPressEvent":
                self.OnMiddleButtonDown()
                button = 'middle'

            self.on_click(prop=pick, button=button)

        if event == "LeftButtonPressEvent":
            self.OnLeftButtonDown()
        elif event == "RightButtonPressEvent":
            self.OnRightButtonDown()
        elif event == "MiddleButtonPressEvent":
            self.OnMiddleButtonDown()


class StyleRubberBandZoom(vtk.vtkInteractorStyleRubberBandZoom):
    pass

class StyleMeshCurveSelection(vtk.vtkInteractorStyleTrackballCamera):

    def __init__(self, on_selected=None):
        self.on_selected = on_selected
        self.points = list()
        self.start_pos = None
        self.end_pos = None
        self.moving = False
        self.world_picker = vtk.vtkWorldPointPicker()

        self.prev_idx = None

        self.mapper = vtk.vtkPolyDataMapper()
        self.actor = vtk.vtkActor()
        self.actor.SetMapper(self.mapper)
        self.actor.GetProperty().SetLineWidth(3)
        self.actor.GetProperty().SetColor(1, 0, 0)

        self.AddObserver("LeftButtonPressEvent", self.on_left_button_press_event)
        self.AddObserver("LeftButtonReleaseEvent", self.on_left_button_release_event)
        self.AddObserver("RightButtonPressEvent", self.on_right_button_press_event)
        self.AddObserver("MouseMoveEvent", self.on_mouse_move_event)
        self.register_callback(vtk.vtkCommand.EndInteractionEvent, self.on_end_interaction)

    def on_end_interaction(self, caller, event):
        if len(self.style.points) > 4:
            contour = self.style.as_polydata()
            nx, ny, nz = self.style.view_vector
            extrude = vtk.vtkLinearExtrusionFilter()
            extrude.SetInputData(contour)
            extrude.SetExtrusionTypeToVectorExtrusion()
            extrude.SetVector(-nx, -ny, -nz)
            extrude.Update()
            res = Mesh(extrude.GetOutput())
            res.fill_holes(inplace=True)
            if self.on_selected:
                self.on_selected(res)

    def set_mesh(self, mesh):
        self.points.clear()
        self.mesh = mesh
        self.locator = vtk.vtkPointLocator()
        self.locator.SetDataSet(mesh)
        self.locator.BuildLocator()

    def find_point_idx(self, coord):
        return self.locator.FindClosestPoint(coord)

    @property
    def interactor(self):
        return self.GetInteractor()

    @property
    def renderer(self):
        return self.GetInteractor().GetRenderWindow().GetRenderers().GetFirstRenderer()

    @property
    def window(self):
        return self.GetInteractor().GetRenderWindow()

    def pick(self):
        point = self.interactor.GetEventPosition()
        self.world_picker.Pick(point[0], point[1], 0, self.renderer)
        return self.world_picker.GetPickPosition()

    def add_point(self):
        world_point = self.pick()
        idx = self.find_point_idx(world_point)
        point = self.mesh.points[idx]
        if self.prev_idx:
            idxs = find_geodesic(self.mesh,
                                 self.prev_idx,
                                 idx)
            self.points.extend(idxs.points.tolist())
        else:
            self.points.append(point)
        self.prev_idx = idx

    def as_polydata(self):
        poly_data = vtk.vtkPolyData()
        pts_ = vtk.vtkPoints()
        for x, y, z in self.points:
            pts_.InsertNextPoint((x, y, z))
        lines = vtk.vtkCellArray()
        lines.InsertNextCell(len(self.points))
        for i in range(len(self.points)):
            lines.InsertCellPoint(i)
        poly_data.SetPoints(pts_)
        poly_data.SetLines(lines)
        return Mesh(poly_data)

    def on_mouse_move_event(self, caller, event):
        if self.interactor and self.moving:
            self.add_point()
            self.draw_polygon()

    def on_left_button_press_event(self, caller, event):
        if self.interactor:
            self.moving = True
            self.add_point()
            self.renderer.AddActor(self.actor)

            self.InvokeEvent(vtk.vtkCommand.StartInteractionEvent)

    def on_left_button_release_event(self, caller, event):
        if self.interactor and self.moving:
            self.moving = False
            self.InvokeEvent(vtk.vtkCommand.SelectionChangedEvent)
            self.InvokeEvent(vtk.vtkCommand.EndInteractionEvent)

    def on_right_button_press_event(self, caller, event):
        self.points.clear()
        self.prev_idx = None
        self.draw_polygon()

    def draw_polygon(self):
        '''Собственно само рисование полигона'''
        self.mapper.SetInputData(self.as_polydata())
        self.window.Render()


class StyleDrawPolygon(vtk.vtkInteractorStyleTrackballCamera):

    def __init__(self, on_select=None, depth=10):
        self.on_select = on_select
        self.depth = depth
        self.points = list()  # Для начала выделение не содержит точек
        self.start_pos = None
        self.end_pos = None
        self.moving = False
        self.world_picker = vtk.vtkWorldPointPicker()

        self.mapper = vtk.vtkPolyDataMapper2D()
        self.actor = vtk.vtkActor2D()
        self.actor.SetMapper(self.mapper)
        self.actor.GetProperty().SetLineWidth(3)
        self.actor.GetProperty().SetColor(1, 0, 0)

        self.AddObserver("LeftButtonPressEvent", self.on_left_button_press_event)
        self.AddObserver("LeftButtonReleaseEvent", self.on_left_button_release_event)
        self.AddObserver("MouseMoveEvent", self.on_mouse_move_event)
        self.AddObserver("EndInteractionEvent", self.on_end_interaction)

    def on_end_interaction(self, caller, event):
        if len(self.points) > 4:
            contour = self.as_polydata()
            nx, ny, nz = self.view_vector
            extrude = vtk.vtkLinearExtrusionFilter()
            extrude.SetInputData(contour)
            extrude.SetExtrusionTypeToVectorExtrusion()
            extrude.SetVector(-nx, -ny, -nz)
            extrude.Update()
            res = Mesh(extrude.GetOutput())
            res.fill_holes(inplace=True)
            res.reverse_sense(inplace=True)
            if self.on_select:
                self.on_select(res)

    @property
    def interactor(self):
        return self.GetInteractor()

    @property
    def renderer(self):
        return self.GetInteractor().GetRenderWindow().GetRenderers().GetFirstRenderer()

    @property
    def window(self):
        return self.GetInteractor().GetRenderWindow()

    @property
    def camera(self):
        return self.renderer.GetActiveCamera()

    @property
    def size(self):
        return self.window.GetSize()

    @property
    def view_vector(self):
        fp = self.camera.GetFocalPoint()
        pos = self.camera.GetPosition()
        vec = [pos[0] - fp[0], pos[1] - fp[1], pos[2] - fp[2]]
        return vec

    def pick(self):
        point = self.interactor.GetEventPosition()
        self.world_picker.Pick(point[0], point[1], 0, self.renderer)
        return self.world_picker.GetPickPosition()

    def as_polydata(self, screen=False):
        poly_data = vtk.vtkPolyData()
        coord = vtk.vtkCoordinate()
        if len(self.points) > 2:
            pts_ = vtk.vtkPoints()
            for x, y, z in self.points:
                if screen:
                    coord.SetCoordinateSystemToWorld()
                    coord.SetValue(x, y, z)
                    x0, y0 = coord.GetComputedDisplayValue(self.renderer)
                    pts_.InsertNextPoint((x0, y0, 0))
                else:
                    pts_.InsertNextPoint((x, y, z))
            lines = vtk.vtkCellArray()
            lines.InsertNextCell(len(self.points) + 1)
            for i in range(len(self.points)):
                lines.InsertCellPoint(i)
            lines.InsertCellPoint(0)
            poly_data.SetPoints(pts_)
            poly_data.SetLines(lines)
        return Mesh(poly_data)

    def on_mouse_move_event(self, caller, event):
        if self.interactor and self.moving:
            self.end_pos = self.pick()
            last_point = self.points[-1]
            new_point = list(self.end_pos)

            if point_distance(last_point, new_point) > 1.0:
                new_point[0] += 0.1 * self.view_vector[0]
                new_point[1] += 0.1 * self.view_vector[1]
                new_point[2] += 0.1 * self.view_vector[2]
                self.points.append(new_point)
            self.draw_polygon()

    def on_left_button_press_event(self, caller, event):
        if self.interactor:
            self.mapper.SetInputData(Mesh())
            self.renderer.AddActor(self.actor)
            self.window.Render()

            self.moving = True
            self.start_pos = self.end_pos = self.pick()
            self.points.clear()
            self.points.append(self.start_pos)

            self.InvokeEvent(vtk.vtkCommand.StartInteractionEvent)

    def on_left_button_release_event(self, caller, event):
        if self.interactor and self.moving:
            self.moving = False
            self.renderer.RemoveActor(self.actor)
            self.window.Render()
            self.InvokeEvent(vtk.vtkCommand.SelectionChangedEvent)
            self.InvokeEvent(vtk.vtkCommand.EndInteractionEvent)

    def draw_polygon(self):
        '''Собственно само рисование полигона'''
        self.mapper.SetInputData(self.as_polydata(screen=True))
        self.window.Render()

class StyleDrawPolygon2(vtk.vtkInteractorStyleTrackballCamera):

    def __init__(self, on_select=None, depth=10):
        self.on_select = on_select
        self.depth = depth
        self.points = list()  # Для начала выделение не содержит точек
        self.start_pos = None
        self.end_pos = None
        self.moving = False
        self.world_picker = vtk.vtkWorldPointPicker()

        self.mapper = vtk.vtkPolyDataMapper()
        self.actor = vtk.vtkActor()
        self.actor.SetMapper(self.mapper)
        self.actor.GetProperty().SetLineWidth(3)
        self.actor.GetProperty().SetColor(1, 0, 0)

        self.AddObserver("LeftButtonPressEvent", self.on_left_button_press_event)
        self.AddObserver("LeftButtonReleaseEvent", self.on_left_button_release_event)
        self.AddObserver("MouseMoveEvent", self.on_mouse_move_event)
        self.AddObserver("EndInteractionEvent", self.on_end_interaction)

    def on_end_interaction(self, caller, event):
        if len(self.points) > 4:
            contour = self.as_polydata()
            nx, ny, nz = self.view_vector
            extrude = vtk.vtkLinearExtrusionFilter()
            extrude.SetInputData(contour)
            extrude.SetExtrusionTypeToVectorExtrusion()
            extrude.SetVector(-nx, -ny, -nz)
            extrude.Update()
            res = Mesh(extrude.GetOutput())
            res.fill_holes(inplace=True)
            res.reverse_sense(inplace=True)
            if self.on_select:
                self.on_select(res)

    @property
    def interactor(self):
        return self.GetInteractor()

    @property
    def renderer(self):
        return self.GetInteractor().GetRenderWindow().GetRenderers().GetFirstRenderer()

    @property
    def window(self):
        return self.GetInteractor().GetRenderWindow()

    @property
    def camera(self):
        return self.renderer.GetActiveCamera()

    @property
    def size(self):
        return self.window.GetSize()

    @property
    def view_vector(self):
        fp = self.camera.GetFocalPoint()
        pos = self.camera.GetPosition()
        vec = [pos[0] - fp[0], pos[1] - fp[1], pos[2] - fp[2]]
        return vec_normalize(vec)

    def pick(self):
        point = self.interactor.GetEventPosition()
        self.world_picker.Pick(point[0], point[1], 0, self.renderer)
        return self.world_picker.GetPickPosition()

    def as_polydata(self):
        poly_data = vtk.vtkPolyData()

        if len(self.points) > 2:
            pts_ = vtk.vtkPoints()
            for x, y, z in self.points:
                pts_.InsertNextPoint((x, y, z))
            lines = vtk.vtkCellArray()
            lines.InsertNextCell(len(self.points) + 1)
            for i in range(len(self.points)):
                lines.InsertCellPoint(i)
            lines.InsertCellPoint(0)
            poly_data.SetPoints(pts_)
            poly_data.SetLines(lines)
        return Mesh(poly_data)

    def on_mouse_move_event(self, caller, event):
        if self.interactor and self.moving:
            self.end_pos = self.pick()
            last_point = self.points[-1]
            new_point = list(self.end_pos)

            if point_distance(last_point, new_point) > 1.0:
                new_point[0] += 0.1 * self.view_vector[0]
                new_point[1] += 0.1 * self.view_vector[1]
                new_point[2] += 0.1 * self.view_vector[2]
                self.points.append(new_point)
            self.draw_polygon()

    def on_left_button_press_event(self, caller, event):
        if self.interactor:
            self.mapper.SetInputData(Mesh())
            self.renderer.AddActor(self.actor)
            self.window.Render()

            self.moving = True
            self.start_pos = self.end_pos = self.pick()
            self.points.clear()
            self.points.append(self.start_pos)

            self.InvokeEvent(vtk.vtkCommand.StartInteractionEvent)

    def on_left_button_release_event(self, caller, event):
        if self.interactor and self.moving:
            self.moving = False
            self.renderer.RemoveActor(self.actor)
            self.window.Render()
            self.InvokeEvent(vtk.vtkCommand.SelectionChangedEvent)
            self.InvokeEvent(vtk.vtkCommand.EndInteractionEvent)

    def draw_polygon(self):
        '''Собственно само рисование полигона'''
        self.mapper.SetInputData(self.as_polydata())
        self.window.Render()


class StyleDrawPolygon3(vtk.vtkInteractorStyleTrackballCamera):

    def __init__(self, interactor=None, on_select=None):
        self.on_select = on_select
        self.world_points = list()  # Для начала выделение не содержит точек
        self.display_points = list()
        self.moving = False
        self.interactor=interactor

        self.picker = vtk.vtkWorldPointPicker()
        self.mapper = vtk.vtkPolyDataMapper2D()
        self.actor = vtk.vtkActor2D()
        self.actor.SetMapper(self.mapper)
        self.actor.GetProperty().SetLineWidth(3)
        self.actor.GetProperty().SetColor(1, 0, 0)

        self.AddObserver("LeftButtonPressEvent", self.on_left_button_press_event)
        self.AddObserver("LeftButtonReleaseEvent", self.on_left_button_release_event)
        self.AddObserver("MouseMoveEvent", self.on_mouse_move_event)


    @property
    def renderer(self):
        return self.interactor.GetRenderWindow().GetRenderers().GetFirstRenderer()

    @property
    def window(self):
        return self.interactor.GetRenderWindow()

    @property
    def camera(self):
        return self.renderer.GetActiveCamera()

    @property
    def size(self):
        return self.window.GetSize()

    @property
    def view_vector(self):
        fp = self.camera.GetFocalPoint()
        pos = self.camera.GetPosition()
        vec = [pos[0] - fp[0], pos[1] - fp[1], pos[2] - fp[2]]
        return vec

    def update_points(self):
        dx, dy = self.interactor.GetEventPosition()
        self.picker.Pick(dx, dy, 0, self.interactor.GetRenderWindow().GetRenderers().GetFirstRenderer())
        self.display_points.append((dx, dy, 0))
        wx, wy, wz = self.picker.GetPickPosition()
        self.world_points.append((wx, wy, wz))

    def on_mouse_move_event(self, caller, event):
        if self.interactor and self.moving:
            pos = self.interactor.GetEventPosition()
            if point_distance(pos, self.display_points[-1][:2]) > 1.0:
                self.update_points()

            self.draw_polygon()

    def on_left_button_press_event(self, caller, event):
        if self.interactor:
            self.mapper.SetInputData(Mesh())
            self.renderer.AddActor(self.actor)

            self.moving = True
            self.display_points.clear()
            self.world_points.clear()
            self.update_points()
            self.InvokeEvent(vtk.vtkCommand.StartInteractionEvent)

    def on_left_button_release_event(self, caller, event):
        if self.interactor and self.moving:
            self.moving = False
            if self.on_select:
                contour_mesh = Mesh.from_points(self.world_points)
                body = contour_mesh.vector_extrude(direction=self.view_vector)
                body.reverse_sense(inplace=True)
                body.fill_holes(inplace=True)
                self.on_select(body)
            self.renderer.RemoveActor(self.actor)
            self.window.Render()
            self.InvokeEvent(vtk.vtkCommand.SelectionChangedEvent)
            self.InvokeEvent(vtk.vtkCommand.EndInteractionEvent)

    def draw_polygon(self):
        contour = Mesh.from_points(points_list=self.display_points)
        self.mapper.SetInputData(contour)
        self.window.Render()


class StyleRubberBand2D(vtk.vtkInteractorStyleRubberBand2D):

    def __init__(self, on_selection=None):
        super().__init__()
        self.on_selection = on_selection
        self.picker = vtk.vtkAreaPicker()
        #self.interactor.SetPicker(self.picker)
        self.AddObserver(vtk.vtkCommand.SelectionChangedEvent, self.callback)

    @property
    def interactor(self):
        return self.GetInteractor()

    @property
    def renderer(self):
        return self.GetInteractor().GetRenderWindow().GetRenderers().GetFirstRenderer()

    @property
    def window(self):
        return self.GetInteractor().GetRenderWindow()

    def callback(self, caller, event):
        if self.on_selection:
            x0, y0 = self.GetStartPosition()
            x1, y1 = self.GetEndPosition()

            if self.picker.AreaPick(x0, y0, x1, y1, self.renderer):
                self.on_selection(self.picker.GetFrustum())

class CircleSelection(vtk.vtkInteractorStyleTrackballCamera):

    def __init__(self, interactor, on_selected=None):
        super().__init__()
        self.on_selected = on_selected
        self.mesh = None
        # Настройки интерактора
        self.interactor = interactor
        self.SetInteractor(self.interactor)

        # Настройки пикера
        self.world_picker = vtk.vtkWorldPointPicker()
        self.interactor.SetPicker(self.world_picker)

        self.selection_actor = None
        self.selection_mesh = None
        self.start_pos = None
        self.end_pos = None
        self.moving = False
        self.selection_indexes = []

        self.AddObserver("LeftButtonPressEvent", self.button_press)
        self.AddObserver("LeftButtonReleaseEvent", self.button_release)
        self.AddObserver("MouseMoveEvent", self.mouse_move)

    def set_mesh(self, mesh):
        self.mesh = mesh.compute_original_ids()

    @property
    def renderer(self):
        return self.interactor.GetRenderWindow().GetRenderers().GetFirstRenderer()

    @property
    def window(self):
        return self.interactor.GetRenderWindow()

    @property
    def current_point(self):
        point = self.interactor.GetEventPosition()
        self.world_picker.Pick(point[0], point[1], 0, self.renderer)
        return self.world_picker.GetPickPosition()

    @property
    def radius(self):
        return point_distance(self.start_pos, self.end_pos)

    @property
    def center(self):
        return self.start_pos

    def button_press(self, caller, event):
        self.start_pos = self.current_point
        self.moving = True
        self.selection_indexes.clear()
        if self.selection_actor:
            self.renderer.RemoveActor(self.selection_actor)
            self.selection_actor = None

        self.InvokeEvent(vtk.vtkCommand.StartInteractionEvent)

    def button_release(self, caller, event):
        self.moving = False
        if self.on_selected:
            self.on_selected(self.start_pos, self.selection_indexes)
        self.InvokeEvent(vtk.vtkCommand.SelectionChangedEvent)
        self.InvokeEvent(vtk.vtkCommand.EndInteractionEvent)

    def mouse_move(self, caller, event):
        if self.moving:
            self.end_pos = self.current_point
            radius = point_distance(self.start_pos, self.end_pos)
            sphere = vtk.vtkSphereSource()
            sphere.SetRadius(radius)
            sphere.SetCenter(self.start_pos)
            self.selection_mesh = self.mesh.select_sphere(center=self.start_pos, radius=radius)
            self.selection_mesh = self.selection_mesh.filter_visible(renderer=self.renderer)
            self.selection_indexes = self.selection_mesh.get_original_ids()

            if not self.selection_actor:
                self.selection_actor = PolyActor(mesh=self.selection_mesh, color='green', vertex_visibility=True, point_size=4.0)
                self.renderer.AddActor(self.selection_actor)
            else:
                self.selection_actor.mesh = self.selection_mesh

            self.window.Render()
