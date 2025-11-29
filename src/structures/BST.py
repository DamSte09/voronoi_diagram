
class Root:
    def __init__(self, node=None):
        self.node = node

    def show_all_leafs(self):
        all_leafs = []
        curr = self.node
        while isinstance(curr, Node):
            curr = curr.left_child
        first_leaf = curr
        succ = successor(first_leaf)
        all_leafs.extend([first_leaf, succ])
        while succ is not None:
            succ = successor(succ)
            if succ is None:
                break
            all_leafs.append(succ)
        
        print("All centres from leaves: ", [leaf.centre for leaf in all_leafs])


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

    def replace_vanishing_leaf(self, leaf, left_point, right_point):
        """Removes fading leaf which represent fading arc in BST
        After leaf is removed, points in grandparent node are updated.
        
        :param leaf: Leaf which represnts fading arc
        """
        # parent of leaf
        leaf_parent = leaf.parent
        
        # Find which child is actual leaf
        if leaf_parent.left_child == leaf:
            replacement = leaf_parent.right_child
        else:
            replacement = leaf_parent.left_child
            
        # Is leaf_parent root
        if leaf_parent.parent is None:
            replacement.parent = None
        else:
            # Grandparent is now parent of replacement
            replacement.parent = leaf_parent.parent
            new_parent = replacement.parent
            new_parent.left_point = left_point 
            new_parent.right_point = right_point 

            # Check which child new replacement is and replaces child
            if leaf_parent.parent.right_child == leaf_parent:
                leaf_parent.parent.right_child = replacement
            else:
                leaf_parent.parent.left_child = replacement
                
            #Updates points in nodes
            # if replacement.parent.left_child == replacement:
            #     current = replacement
                
            #     while isinstance(current, Node):
            #         current = current.right_child

            #     replacement.parent.left_point = current.centre
            # else:
            #     current = replacement
                
            #     while isinstance(current, Node):
            #         current = current.left_child

            #     replacement.parent.right_point = current.centre
            #     


        leaf.parent = None
        leaf_parent.left_child = None
        leaf_parent.right_child = None
        leaf_parent.parent = None

        

class Leaf:
    """Lowest node of a tree, keeps centre which define arc"""
    def __init__(self, point: list):
        self.centre = point
        self.parent = None
        self.circle_event = None

   
            


def successor(leaf: Leaf) -> Leaf | None:
    curr = leaf

    while curr.parent and curr == curr.parent.right_child:
        curr = curr.parent

    if not curr.parent:
        return None

    curr = curr.parent.right_child

    while isinstance(curr, Node):
        curr = curr.left_child

    return curr
