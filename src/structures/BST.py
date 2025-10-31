
class Node:
    """Break point on beachline, keeps 2 sorted centres by x,
      left defines left arc, right - right arc
      if parent is none then it is root
    """
    def __init__(self, left_point, right_point):
        self.left_point = left_point
        self.right_point = right_point
        self.parent = None 
        self.left_child = None 
        self.right_child = None
        self.half_edge = None
        

class Leaf:
    """Keep centre which define arc"""
    def __init__(self, point):
        self.centre = point
        self.parent = None
        self.circle_event = None




