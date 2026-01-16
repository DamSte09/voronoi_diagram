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
        
    def bound_area(self):
        min_x = min(p[0] for p in self.points)
        max_x = max(p[0] for p in self.points)
        dx = max_x - min_x

        min_y = min(p[1] for p in self.points)
        max_y = max(p[1] for p in self.points)
        dy = max_y - min_y
        
        M = max(dx, dy)
        
        box = [
            [min_x - M, min_y - M], 
            [max_x + M, min_y - M], 
            [max_x + M, max_y + M],
            [min_x - M, max_y + M], 
            ]
        
        return box

    def close_halfedges(self, generator_pairs):
        for i, he in enumerate(self.half_edges):
            if he.twin.origin is None:
                origin = (he.origin[0], he.origin[1])
                A, B = generator_pairs[i]
                direction = self.normalize(self.perpendicular_vector(A, B))
                
                bounding_box = self.bound_area()
                
                intersection = self.intersect_ray_with_box(origin, direction, bounding_box)
                if intersection is None:
                    continue
                
                V = Vertex(intersection)
                self.vertices.append(V)
                he.twin.origin = V

    @staticmethod
    def normalize(v):
        length = math.hypot(v[0], v[1])
        return (v[0]/length, v[1]/length)

    @staticmethod
    def perpendicular_vector(a, b):
        dx = b[0] - a[0]
        dy = b[1] - a[1]
        return (-dy, dx)

    @staticmethod
    def intersect_ray_with_box(origin, direction, box):
        x0, y0 = origin
        dx, dy = direction
        x_min, y_min = box[0]
        x_max, y_max = box[2]

        t_values = []
        if dx != 0:
            t_left = (x_min - x0) / dx
            t_right = (x_max - x0) / dx
            t_values.extend([t for t in (t_left, t_right) if t > 0])
        if dy != 0:
            t_bottom = (y_min - y0) / dy
            t_top = (y_max - y0) / dy
            t_values.extend([t for t in (t_bottom, t_top) if t > 0])

        if not t_values:
            return None

        t = min(t_values)  
        return (x0 + dx * t, y0 + dy * t)

    def fillup_faces(self):
        for he in self.half_edges:
            if he.face is None:
                starting_halfedge = he
                face = Face()
                face.outer_component = starting_halfedge

                he = starting_halfedge
                while True:
                    he.face = face
                    he = he.next
                    if he == starting_halfedge:
                        break

                self.faces.append(face)




