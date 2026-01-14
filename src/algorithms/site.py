from src.structures.BST import Leaf, Node, Root
from src.structures.QE import CircleEvent, SiteEvent, EventsQueue
from src.structures.DCEL import DCEL, HalfEdge, Vertex, Face
import math

def handle_site_event(root: Root, new_event: SiteEvent, queue: EventsQueue, dcel: DCEL, y_sweep: float):

    # 1. step, when BST is empty, we insert a leaf as root
    if root.node is None or root is None:
        root.node = Leaf(new_event.centre)
        print("First met point: ", root.node.centre)
        return root 
            
    # Finds leaf of arc from beach line above the new point
    arc_above = find_arc_above(root, new_event, y_sweep)
    print("point of arc above: ", arc_above.centre)

    # Removes false alarm
    if arc_above.circle_event is not None:
        queue.remove_from_queue(arc_above.circle_event)
        arc_above.circle_event = None

    parent_arc_above = arc_above.parent

    # Replace leaf with arc above with new subtree
    new_subtree, dcel = replace_with_subtree(arc_above, new_event.centre)

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

    #new_subtree = dcel.add_site_halfedges(new_event.centre, new_subtree)
    print(new_subtree.half_edge, new_subtree.right_child.half_edge)

    print("DCEL faces after added halfedges:", [p.centre for p in dcel.faces])
    print("DCEL halfedges:", dcel.half_edges)
    
    # Finding predecessor and successor
    left_neighbour = new_subtree.left_child.predecessor()
    right_neighbour = new_subtree.right_child.right_child.successor()

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

        check_circle_event(right_three_arcs, y_sweep, queue)
        check_circle_event(left_three_arcs, y_sweep, queue)

    root.show_all_leafs()

    return root

def find_arc_above(root: Root, event: SiteEvent, y_sweep:float):
    """Finds arc above new found point by sweepline in BST"""
    curr = root.node
    new_point = event.centre
    while isinstance(curr, Node):
        print("actual points of node:", curr.left_point, curr.right_point)

        xb = curr.count_x_breakpoint(y_sweep)
        print("breakpoint:", xb)
        
        if  new_point[0] <= xb:
            curr = curr.left_child
        else:
            curr = curr.right_child
        
    print("\nFound leaf above point:", curr.centre, "\n")
    return curr

def replace_with_subtree(arc_above: Leaf, new_centre: list, dcel: DCEL):
    """Replaces leaf of arc above new centre with subtree with 3 leafs:
    arc_above, new_centre, arc_above

    Schema of a subtree: # TO SIĘ ZMIENIŁO
        N(j, i)
        /\
    L(j) N(i, j)
          /\
        L(i) L(j)

    :param arc_above: Contains leaf of an arc above the new centre
    :param new_centre: New found point by sweep line
    """
    point_j = arc_above.centre
    point_i = new_centre

    # Creating leaves
    left_leaf = Leaf(point_j)
    right_leaf = Leaf(point_j)
    mid_leaf = Leaf(point_i)

    # Root of new subtree
    subtree_root = Node(left_point=left_leaf.centre,
                        right_point=mid_leaf.centre)
    print("Subtree root points:", subtree_root.left_point, subtree_root.right_point)

    subtree_root.left_child = left_leaf
    left_leaf.parent = subtree_root

    # Right node of the subtree
    # THERE SHOULD BE CHECKING INTERSECTION BETWEEN POINTS but not now
    right_node = Node(
        left_point=mid_leaf.centre, right_point=right_leaf.centre
    )

    right_node.parent = subtree_root
    subtree_root.right_child = right_node

    right_node.left_child = mid_leaf
    right_node.right_child = right_leaf

    mid_leaf.parent = right_node
    right_leaf.parent = right_node

    # Creating half edges records
    A, B = point_j, point_i

    # Tuple of points representing breakpoint
    AB = (point_j, point_i)
    BA = (point_i, point_j)

    edge_AB = HalfEdge()
    edge_BA = HalfEdge()

    edge_AB.origin = AB
    edge_BA.origin = BA

    face_A = dcel.add_face(A)
    face_B = dcel.add_face(B) 

    edge_AB.face = face_B
    edge_BA.face = face_A

    face_A.outer_component = face_A.outer_component or edge_AB
    face_B.outer_component = face_B.outer_component or edge_BA

    edge_AB.twin = edge_BA
    edge_BA.twin = edge_AB

    subtree_root.half_edge = edge_AB
    right_node.half_edge = edge_BA

    dcel.half_edges.extend([edge_AB, edge_BA])

    return subtree_root

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
    if ux is None or uy is None:
        return None
    
    print("CC", ux, uy)
    r = math.sqrt( ( ux - A[0] ) ** 2 + (uy - A[1])**2)
    event_y = uy - r # lowest point of circle
    
    # Condition that that event cannot be higher than y_sweep
    if not math.isfinite(event_y) or event_y >= y_sweep:
        return None
    
    if getattr(b, "circle_event", None) is not None:
        queue.remove_from_queue(b.circle_event)
        b.circle_event = None

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

    if d == 0:
        return None, None

    ux = ((Ax**2 + Ay**2)*(By - Cy) +
          (Bx**2 + By**2)*(Cy - Ay) +
          (Cx**2 + Cy**2)*(Ay - By)) / d
    uy = ((Ax**2 + Ay**2)*(Cx - Bx) +
          (Bx**2 + By**2)*(Ax - Cx) +
          (Cx**2 + Cy**2)*(Bx - Ax)) / d
    print("Circle center:", ux, uy)
    return ux, uy


    