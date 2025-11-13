
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

    def balance_tree(self):
        pass 

        

class Leaf:
    """Lowest node of a tree, keeps centre which define arc"""
    def __init__(self, point: list):
        self.centre = point
        self.parent = None
        self.circle_event = None

    def remove_leaf(self):
        parent = self.parent

        if parent.left_child == self:
            parent.left_child = None
        elif parent.right_child == self:
            parent.right_child = None

        self.parent = None


