
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

    def remove_leaf(self, leaf):
        """Removes fading leaf which represent fading arc in BST
        
        :param leaf: Leaf which represnts fading arc
        """
        leaf_parent = leaf.parent
        
        if leaf_parent.left_child == leaf:
            replacement = leaf_parent.right_child
        else:
            replacement = leaf_parent.left_child
            
        # Grandparent is now parent of replacement
        replacement.parent = leaf_parent.parent

        # Check which child new replacement is and replaces child
        if leaf_parent.parent.right_child == leaf_parent:
            leaf_parent.parent.right_child = replacement
        else:
            leaf_parent.parent.left_child = replacement
            
        #Updates points in nodes
        if replacement.parent.left_child == replacement:
            current = replacement
            
            while isinstance(current, Node):
                current = current.right_child

            replacement.parent.left_point = current.centre
        else:
            current = replacement
            
            while isinstance(current, Node):
                current = current.left_child

            replacement.parent.right_point = current.centre

            
        leaf_parent = None

        

class Leaf:
    """Lowest node of a tree, keeps centre which define arc"""
    def __init__(self, point: list):
        self.centre = point
        self.parent = None
        self.circle_event = None

   
            


