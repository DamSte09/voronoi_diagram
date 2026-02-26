import math
from src.structures.BST import Node


class Vertex:
    def __init__(self, point: list):
        self.x = point[0]
        self.y = point[1]
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
    
    def add_vertex(self, point):
        v = Vertex(point)
        self.vertices.append(v)
        
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

    def close_halfedges(self, points):
        box = DCEL.bound_area(points)

        for he in self.half_edges:
            # Skip if edge is already bounded or invalid
            if he.origin is None or he.twin is None or he.twin.origin is not None:
                continue

            if he.face is None or he.twin.face is None:
                continue

            origin = (he.origin.x, he.origin.y)
            A = he.face.centre  # Site on the left of the half-edge
            B = he.twin.face.centre  # Site on the right of the half-edge

            # The Voronoi edge lies on the perpendicular bisector of segment AB
            # Get perpendicular direction (rotated 90 degrees)
            dx = B[0] - A[0]
            dy = B[1] - A[1]
            perp = (dy, dx)  # Perpendicular vector
            
            # The midpoint between the two sites
            mid = ((A[0] + B[0]) / 2, (A[1] + B[1]) / 2)
            
            # Vector from midpoint to the known origin of the edge
            to_origin = (origin[0] - mid[0], origin[1] - mid[1])
            
            # Determine which direction the unbounded edge extends from origin
            # We need to go in the direction AWAY from the origin point
            # If the perpendicular vector points in the same direction as to_origin,
            # we need to reverse it to point away
            dot = perp[0] * to_origin[0] + perp[1] * to_origin[1]
            
            if dot > 0:
                # perp points towards origin, we need to go the opposite way
                direction = DCEL.normalize((-perp[0], -perp[1]))
            else:
                # perp points away from origin, this is correct
                direction = DCEL.normalize(perp)

            # Find intersection with bounding box
            endpoint = DCEL.intersect_ray_with_box(origin, direction, box)
            
            if endpoint is None:
                # Fallback: try the opposite direction
                direction = (-direction[0], -direction[1])
                endpoint = DCEL.intersect_ray_with_box(origin, direction, box)
                
            if endpoint is None:
                # Still no intersection, skip this edge
                continue

            # Create vertex at the boundary and assign to twin's origin
            v = Vertex(endpoint)
            self.vertices.append(v)
            he.twin.origin = v

    @staticmethod
    def normalize(v):
        """Normalize a vector to unit length."""
        length = math.hypot(v[0], v[1])
        if length == 0:
            return (0, 0)
        return (v[0]/length, v[1]/length)

    @staticmethod
    def perpendicular_vector(a, b):
        """Get perpendicular vector to the segment from a to b."""
        dx = b[0] - a[0]
        dy = b[1] - a[1]
        return (-dy, dx)

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