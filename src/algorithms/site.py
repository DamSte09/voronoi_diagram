from src.structures.BST import Leaf, Node, Root
from src.structures.QE import CircleEvent, SiteEvent, EventsQueue
from src.structures.DCEL import DCEL, HalfEdge, Vertex, Face
import math

def handle_site_event(root: Root, new_event: SiteEvent, queue: EventsQueue, dcel: DCEL):

    # 1. step, when BST is empty
    if root.node is None:
        root.node = Leaf(new_event.centre)
        dcel.add_face(new_event.centre)
        print("First met event: ", root.node.centre)
        return root 
    
    # For second met event
    if isinstance(root.node, Leaf):
        child = root.node
        new_point = new_event.centre

        if child.centre[0] < new_point[0]:
            root.node = Node(left_point=child.centre, right_point=new_point)
            root.node.left_child = Leaf(child.centre)
            root.node.right_child = Leaf(new_point)
        else:
            root.node = Node(left_point=new_point, right_point=child.centre)
            root.node.right_child = Leaf(child.centre)
            root.node.left_child = Leaf(new_point)

        root.node.left_child.parent = root.node
        root.node.right_child.parent = root.node
        print("Left point in root node: ", root.node.left_point)
        print("Right point in root node: ", root.node.right_point)

        dcel.add_face(new_event.centre)

        print("Faces in DCEL: ", [p.centre for p in dcel.faces])
        return root
            
    # For third and above met points
    arc_above = find_arc_above(root, new_event.centre)
    print("arc above: ", arc_above.centre)
 
    dcel.add_face(new_event.centre)

    if arc_above.circle_event is not None:
        queue.remove_from_queue(arc_above.circle_event)
        arc_above.circle_event = None
    
    parent_arc_above = arc_above.parent

    # Exchanging leaf with arc above with new subtree
    new_subtree = replace_with_subtree(arc_above, new_event.centre)

    if parent_arc_above is None:
        root.node = new_subtree
        new_subtree.parent = None
    else:
        if parent_arc_above.left_child == arc_above:
            parent_arc_above.left_child = new_subtree
        else:
            parent_arc_above.right_child = new_subtree 

        new_subtree.parent = parent_arc_above

    print("Left arc of a new subtree root:", new_subtree.left_point) 
    print("Middle arc:", new_subtree.right_child.left_child.centre)
    print("Right arc:", new_subtree.right_point)

    new_subtree = dcel.add_site_halfedges(new_event.centre, new_subtree)
    print(new_subtree.half_edge, new_subtree.right_child.half_edge)

    print("DCEL faces after added halfedges:", [p.centre for p in dcel.faces])
    print("DCEL halfedges:", dcel.half_edges)
    
    left_neighbour = predecessor(new_subtree.left_child)
    right_neighbour = successor(new_subtree.right_child.right_child)

    if left_neighbour and right_neighbour:
        left_three_arcs = [
            left_neighbour,
            new_subtree.left_child,
            new_subtree.right_child.left_child,
        ]
        right_three_arcs = [
            new_subtree.right_child.left_child,
            new_subtree.right_child.right_child,
            right_neighbour,
        ]
        y_sweep = new_event.centre[1]

        check_circle_event(right_three_arcs, y_sweep, queue)
        check_circle_event(left_three_arcs, y_sweep, queue)

    root.show_all_leafs()

    return root

def find_arc_above(root: Root, point: list):
    """Finds arc above new found point by sweepline in BST"""
    curr = root.node
    while not isinstance(curr, Leaf):
        x_breakpoint = count_x_breakpoint(curr.left_point, curr.right_point, point[1])
        if x_breakpoint > point[0]:
            curr = curr.left_child
        else:
            curr = curr.right_child
    
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

def replace_with_subtree(arc_above: Leaf, new_centre: list):
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


def balance_tree(root):
    pass

def predecessor(leaf: Leaf) -> Leaf | None:
    curr = leaf

    while curr.parent and curr == curr.parent.left_child:
        curr = curr.parent

    if not curr.parent:
        return None

    curr = curr.parent.left_child

    while isinstance(curr, Node):
        curr = curr.right_child

    return curr


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

def check_circle_event(three_next_leafs: list[Leaf, Leaf, Leaf], y_sweep: float, queue: EventsQueue):
    """Checks if 3 given points are on one circle
    
    :param three_next_leafs: List of 3 next leafs
    """
    a, b, c = three_next_leafs
    A = a.centre
    B = b.centre
    C = c.centre
    
    # Are points are collinear
    EPS = 1e-9
    det = (B[0] - A[0])*(C[1] - A[1]) - (B[1] - A[1])*(C[0] - A[0])

    if abs(det)< EPS:
        print("Points are collinear")
        return None
    
    # Counting centre of a circle
    ux, uy = circle_center(A, B, C)
    r = math.sqrt( ( ux - A[0] ) ** 2 + (uy - A[1])**2)
    event_y = uy - r # lowest point of circle
    
    # Condition that that event cannot be higher than y_sweep
    if event_y >= y_sweep:
        return None

    # Adding middle point as a pointer, bc middle arc will be the one which dissapears
    point = [ux, event_y]
    event = CircleEvent(point= point, leaf_pointer=b)
    b.circle_event = event

    queue.insert_event(event)
    
def circle_center(A, B, C):
    Ax, Ay = A
    Bx, By = B
    Cx, Cy = C
    d = 2 * (Ax * (By - Cy) + Bx * (Cy - Ay) + Cx * (Ay - By))

    ux = ((Ax**2 + Ay**2)*(By - Cy) +
          (Bx**2 + By**2)*(Cy - Ay) +
          (Cx**2 + Cy**2)*(Ay - By)) / d
    uy = ((Ax**2 + Ay**2)*(Cx - Bx) +
          (Bx**2 + By**2)*(Ax - Cx) +
          (Cx**2 + Cy**2)*(Bx - Ax)) / d
    return ux, uy


    