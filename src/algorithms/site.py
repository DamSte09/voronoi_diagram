from src.structures.BST import Leaf, Node, Root
from src.structures.QE import CircleEvent
import math

def handle_site_event(root, new_event, queue, dcel):
    # 1. step, when BST is empty
    if root.node is None:
        root.node = Leaf(new_event)
        dcel.add_face(new_event)
        print("First met point: ", root.node.centre)
        return root 
    
    # For second met centre
    if isinstance(root.node, Leaf):
        child = root.node

        if child.centre[0] < new_event[0]:
            root.node = Node(left_point=child.centre, right_point=new_event)
            root.node.left_child = Leaf(child.centre)
            root.node.right_child = Leaf(new_event)

        else:
            root.node = Node(left_point=new_event, right_point=child.centre)
            root.node.right_child = Leaf(child.centre)
            root.node.left_child = Leaf(new_event)

        root.node.left_child.parent = root.node
        root.node.right_child.parent = root.node
        dcel.add_face(new_event)
        print("Left point in root node: ", root.node.left_point)
        print("Right point in root node: ", root.node.right_point)
        return root
            
    # For third and above met points
    arc_above = find_arc_above(root, new_event)
    print(arc_above.centre)

    # if arc_above.circle_event is True:
    #     remove_from_queue(arc_above.centre, queue)
    
    parent_arc_above = arc_above.parent
    
    # Exchanging leaf with arc above with new subtree 
    if parent_arc_above.left_child == arc_above:
        arc_above = replace_with_subtree(arc_above, new_event)
        parent_arc_above.left_child = arc_above
    else:
        arc_above = replace_with_subtree(arc_above, new_event)
        parent_arc_above.right_child = arc_above 

    arc_above.parent = parent_arc_above
    print("Left arc of a new subtree root:", arc_above.left_point) 
    print("Right arc:", arc_above.right_point)
    print("Middle arc:", arc_above.right_child.left_child.centre)


    # balance_tree(root)
# 
    # dcel.add_new_halfedges(new_event, arc_above)
    # 
    # left_neighbour = predecessor(arc_above.left_child)
    # right_neighbour = successor(arc_above.right_child.right_child)
# 
    # left_three_arcs = [left_neighbour,arc_above.left_child, arc_above.right_child.left_child]
    # right_three_arcs = [arc_above.right_child.left_child, arc_above.right_child.right_child, right_neighbour]
    # y_sweep = new_event[1]
    # 
    # check_circle_event(right_three_arcs, y_sweep, queue)
    # check_circle_event(left_three_arcs, y_sweep, queue)
    
def find_arc_above(root: Root, point: list):
    """Finds arc above new found point by sweepline in BST"""
    curr = root.node
    while not isinstance(curr, Leaf):
        x_breakpoint = count_x_breakpoint(curr.left_point, curr.right_point, point[1])
        if x_breakpoint > point[0]:
            curr = curr.left_child
        else:
            curr = curr.right_child
    
    print(curr.centre)
    return curr

def count_x_breakpoint(left_centre, right_centre, y_sweep):
    """Counts x breakpoint for node of 2 points and sweepline on new centre"""
    x1, y1 = left_centre
    x2, y2 = right_centre

    a = y2 - y1
    b = 2*(-y2*x1 + y1*x2 + y_sweep*x1 - y_sweep*x2)
    c = (y2 - y_sweep)*(x1**2 + y1**2 - y_sweep**2) \
        - (y1 - y_sweep)*(x2**2 + y2**2 - y_sweep**2)

    delta = b**2 - 4*a*c

    x1_bp = (-b+math.sqrt(delta)) / 2*a

    if x1_bp <0:
        x2_bp = (-b-math.sqrt(delta)) / 2*a
        return x2_bp

    return x1_bp

def replace_with_subtree(arc_above: Leaf, new_centre):
    """Replaces leaf of arc above new centre with subtree with 3 leafs:
    arc_above, new_centre, arc_above

    Schema of a subtree:
        N(a, a)
        /\
    L(a) N(p, a)
          /\
        L(p) L(a)

    :param arc_above: Contains leaf of an arc above the new centre
    :param new_centre: New found point by sweep line
    """
    left_leaf = Leaf(arc_above.centre)
    left_leaf.parent = None

    right_leaf = Leaf(arc_above.centre)
    right_leaf.parent = None

    mid_leaf = Leaf(new_centre)

    # Root of new subtree
    subtree_root = Node(left_point=left_leaf.centre, right_point=right_leaf.centre)
    subtree_root.left_child = left_leaf
    left_leaf.parent = subtree_root

    # Right node of the subtree
    subtree_root.right_child = Node(left_point=mid_leaf.centre, right_point=right_leaf.centre)
    subtree_root.right_child.parent = subtree_root

    right_node = subtree_root.right_child

    right_node.left_child = mid_leaf
    right_node.right_child = right_leaf

    mid_leaf.parent = right_node
    right_leaf.parent = right_node

    return subtree_root


# def balance_tree(root):
#     pass

# def predecessor(leaf):
#     curr = leaf

#     while curr.parent and curr == curr.parent.left_child:
#         curr = curr.parent

#     if not curr.parent:
#         return None

#     curr = curr.parent.left_child

#     while isinstance(curr, Node):
#         curr = curr.right_child

#     return curr


# def successor(leaf):
#     curr = leaf

#     while curr.parent and curr == curr.parent.right_child:
#         curr = curr.parent

#     if not curr.parent:
#         return None

#     curr = curr.parent.right_child

#     while isinstance(curr, Node):
#         curr = curr.left_child

#     return curr

# def check_circle_event(three_next_leafs: list[Leaf, Leaf, Leaf], y_sweep, queue):
#     """Checks if 3 given points are on one circle
    
#     :param three_next_leafs: List of 3 next leafs
#     """
#     a, b, c = three_next_leafs
#     A = a.centre
#     B = b.centre
#     C = c.centre
    
#     # Are points are collinear
#     EPS = 1e-9
#     det = (B[0] - A[0])*(C[1] - A[1]) - (B[1] - A[1])*(C[0] - A[0])

#     if abs(det)< EPS:
#         print("No circle event, points are collinear")
#         return None
    
#     # Counting centre of a circle
    
#     ux, uy = circle_center(A, B, C)
#     r = math.sqrt( ( ux - A[0] ) ** 2 + (uy - A[1])**2)
#     event_y = uy - r # lowest point of circle
    
#     # Condition that that event cannot be higher than y_sweep
#     if event_y >= y_sweep:
#         return None

#     # Adding middle point as a pointer, bc middle arc will be the one which dissapears
#     event = CircleEvent([ux, event_y], b)
#     b.circle_event = event

#     queue.insert_event(event)
    
# def circle_center(A, B, C):
#     Ax, Ay = A
#     Bx, By = B
#     Cx, Cy = C
#     d = 2 * (Ax * (By - Cy) + Bx * (Cy - Ay) + Cx * (Ay - By))

#     ux = ((Ax**2 + Ay**2)*(By - Cy) +
#           (Bx**2 + By**2)*(Cy - Ay) +
#           (Cx**2 + Cy**2)*(Ay - By)) / d
#     uy = ((Ax**2 + Ay**2)*(Cx - Bx) +
#           (Bx**2 + By**2)*(Ax - Cx) +
#           (Cx**2 + Cy**2)*(Bx - Ax)) / d
#     return ux, uy


    







# def remove_from_queue(leaf, queue):
#     """Removes event from queue"""
#     all_ce = queue.circle_events
#     if leaf.circle_event is True:
#         all_ce.remove(leaf.circle_event)        
                         
#     queue.circle_events = all_ce 
#     return queue