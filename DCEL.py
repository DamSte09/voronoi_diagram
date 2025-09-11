class DCEL:
    def __init__(self, points):
        self.vertices = []
        self.half_edges = []
        self.faces = []


class Vertex:
    def __init__(self, point:list):
        self.x = point[0] 
        self.y = point[1] 
        self.incident_edge = [] # np. e1,2, aktualne vi to poczatek



class Face:
    def __init__(self):
        self.outer_component = None
        self.inner_component = None
        self.site = None


class HalfEdge:
    def __init__(self):
        self.origin = None # poczatek
        self.twin = None
        self.next = None
        self.prev = None 


        
