import math
from src.structures.BST import Node


class Vertex:
    def __init__(self, point: list, internal: bool = False):
        self.x = point[0]
        self.y = point[1]
        self.internal = internal
        self.incident_edge = []


class Face:
    def __init__(self, centre):
        self.outer_component = None
        self.inner_component = None
        self.centre = centre


class HalfEdge:
    def __init__(self):
        self.origin = None
        self.twin = None
        self.face = None
        self.next = None
        self.prev = None


class DCEL:
    def __init__(self):
        self.vertices = []
        self.half_edges = []
        self.faces = []
    
    def add_face(self, new_centre: list) -> Face:
        """Create face record and appends to list of faces in DCEL
        
        :param new_centre: New met point by sweep
        """
        for f in self.faces:
            if f.centre == new_centre:
                return f

        face_j = Face(new_centre)
        self.faces.append(face_j)
        return face_j
    
    def add_site_halfedges(self, new_centre: list, new_subtree: Node):
        """Adds records of new halfedges to DCEL into list of halfedges.
        
        :param new_centre: New met point by sweep 
        :param new_subtree: Subree made from arc above and new point
        """
        he1 = new_subtree.half_edge
        # drugi breakpoint
        he2 = new_subtree.right_child.half_edge

        # dodajemy je do DCEL
        self.half_edges.extend([he1, he1.twin, he2, he2.twin])

        return new_subtree
    
    @staticmethod
    def bound_area(points):
        min_x = min(p[0] for p in points)
        max_x = max(p[0] for p in points)
        min_y = min(p[1] for p in points)
        max_y = max(p[1] for p in points)

        M = max(max_x - min_x, max_y - min_y)

        return [
            [min_x - M, min_y - M],
            [max_x + M, min_y - M],
            [max_x + M, max_y + M],
            [min_x - M, max_y + M],
        ]

    def finish_edges(self, root, points):
        """Zamyka półproste, które zostały na linii brzegowej po końcu pętli.

        Każdy węzeł (breakpoint) w drzewie to jedna niedomknięta krawędź.
        Breakpoint (A, B) przy miotle schodzącej w dół porusza się
        w kierunku d = (B.y - A.y, A.x - B.x).
        """
        # ramka obejmuje punkty I wierzchołki Voronoia
        all_points = list(points) + [(v.x, v.y) for v in self.vertices]
        box = DCEL.bound_area(all_points)

        # zbieramy wszystkie węzły wewnętrzne
        nodes = []
        stack = [root.node]
        while stack:
            n = stack.pop()
            if isinstance(n, Node):
                nodes.append(n)
                stack.extend([n.left_child, n.right_child])

        # najpierw liczymy, potem modyfikujemy – krawędź bez żadnego
        # wierzchołka ma DWA węzły, które nie mogą sobie przeszkadzać
        pending = []
        for node in nodes:
            A, B = node.left_point, node.right_point
            d = DCEL.normalize((B[1] - A[1], A[0] - B[0]))
            twin_origin = node.half_edge.twin.origin
            if twin_origin is not None:
                start = (twin_origin.x, twin_origin.y)
            else:
                start = ((A[0] + B[0]) / 2, (A[1] + B[1]) / 2)
            pending.append((node.half_edge, start, d))

        for he, start, d in pending:
            end = DCEL.intersect_ray_with_box(start, d, box)
            if end is None:
                continue
            v = Vertex(end, internal=False)
            self.vertices.append(v)
            he.origin = v

    @staticmethod
    def normalize(v):
        """Normalize a vector to unit length."""
        length = math.hypot(v[0], v[1])
        if length == 0:
            return (0, 0)
        return (v[0]/length, v[1]/length)

    @staticmethod
    def intersect_ray_with_box(origin, direction, box):
        """Find the intersection of a ray with a bounding box.
        
        :param origin: (x, y) starting point of the ray
        :param direction: (dx, dy) normalized direction vector
        :param box: bounding box as [bottom-left, bottom-right, top-right, top-left]
        :return: (x, y) intersection point or None if no intersection
        """
        x0, y0 = origin
        dx, dy = direction
        x_min, y_min = box[0]
        x_max, y_max = box[2]

        t_values = []
        
        # Check intersection with vertical boundaries (left and right)
        if abs(dx) > 1e-10:  # Avoid division by zero
            t_left = (x_min - x0) / dx
            t_right = (x_max - x0) / dx
            # Only consider intersections in the forward direction (t > epsilon)
            if t_left > 1e-10:
                y_at_left = y0 + dy * t_left
                if y_min <= y_at_left <= y_max:
                    t_values.append(t_left)
            if t_right > 1e-10:
                y_at_right = y0 + dy * t_right
                if y_min <= y_at_right <= y_max:
                    t_values.append(t_right)
        
        # Check intersection with horizontal boundaries (bottom and top)
        if abs(dy) > 1e-10:  # Avoid division by zero
            t_bottom = (y_min - y0) / dy
            t_top = (y_max - y0) / dy
            # Only consider intersections in the forward direction (t > epsilon)
            if t_bottom > 1e-10:
                x_at_bottom = x0 + dx * t_bottom
                if x_min <= x_at_bottom <= x_max:
                    t_values.append(t_bottom)
            if t_top > 1e-10:
                x_at_top = x0 + dx * t_top
                if x_min <= x_at_top <= x_max:
                    t_values.append(t_top)

        if not t_values:
            return None

        # Take the closest valid intersection
        t = min(t_values)
        return (x0 + dx * t, y0 + dy * t)
