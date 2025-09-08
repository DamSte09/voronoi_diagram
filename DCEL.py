



    

class DCEL:
    def __init__(self, points):
        self.points = points


class Vertice(DCEL):
    def __init__(self):
        self.name_vertice = "" # np. v1 
        self.coordinates = [] # np. [0,4]
        self.incident_edge = [] # np. e1,2, aktualne vi to poczatek



class Face(DCEL):
    def __init__(self):
        self.name_face = ""
        self.outer_component = None
        self.inner_component = None


class HalfEdge(DCEL):
    def __init__(self):
        self.half_edge = ""
        self.origin = "" # poczatek
        self.twin = ""
        self.next = ""
        self.prev = ""


        
