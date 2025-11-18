class DCEL:
    def __init__(self, points):
        self.vertices = []
        self.half_edges = []
        self.faces = []
    
    def add_face(self, new_centre):
        """Create face record and appends to list of faces in DCEL
        
        :param new_centre: New met point by sweep
        """
        face_j = Face(new_centre)
        self.faces.append(face_j)
    
    def add_halfedges_site(self, new_centre, new_subtree):
        """Adds records of new halfedges to DCEL into list of halfedges.
        
        :param new_centre: New met point by sweep 
        :param new_subtree: Subree made from arc above and new point
        """
        p_i = new_centre
        p_j = new_subtree.left_child.centre

        e_ji = HalfEdge()
        e_ij = HalfEdge()
        e_ji.twin = e_ij
        e_ij.twin = e_ji

        face_j = next((f for f in self.faces if f.site == p_j), None)
        face_i = Face(p_i)

        e_ij.face = face_i
        e_ji.face = face_j
        
        self.faces.append(face_i)
        self.half_edges.extend([e_ji, e_ij])


class Vertex:
    def __init__(self, point:list):
        self.x = point[0] 
        self.y = point[1] 
        self.incident_edge = [] 


class Face:
    def __init__(self, site):
        self.outer_component = None
        self.inner_component = None
        self.site = site 


class HalfEdge:
    def __init__(self):
        self.origin = None  # poczatek
        self.twin = None
        self.face = None
        self.next = None
        self.prev = None 


        
