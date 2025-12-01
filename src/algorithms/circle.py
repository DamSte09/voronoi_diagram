import math

from src.structures.QE import EventsQueue
from src.structures.DCEL import DCEL, Vertex, HalfEdge, Face
from src.structures.BST import Leaf, Node
from funcs import successor,predecessor, remove_from_queue, circle_center, check_circle_event

def handle_circle_event(y: Leaf, root: Node, queue: EventsQueue, dcel: DCEL):
    left_leaf = predecessor(y)
    right_leaf = successor(y)

    if not left_leaf or not right_leaf:
        return root
    
    A = left_leaf.centre
    B = y.centre
    C = right_leaf.centre
    
    bp = y.parent
    print(f"A: {A}, B: {B}, C:{C}")

    # should only happen when only B vanished
    cc = circle_center(A, B, C)
    print("Center of a circle: ", cc)

    if cc is None or any(math.isinf(c) or math.isnan(c) for c in cc):
        print("Circle center does not exist")
        return None
    
    V_cc = Vertex(cc)
    dcel.vertices.append(V_cc)

    h_left = bp.half_edge
    h_right = bp.half_edge.twin

    h_right.origin = V_cc

    root.replace_vanishing_leaf(y, A, C)

    new_he = HalfEdge()
    new_het = HalfEdge()
    new_he.twin = new_het
    new_het.twin = new_he

    new_he.origin = V_cc

    h_left.next = new_he
    new_he.prev = h_left

    new_het.next = h_right
    h_right.prev = new_het
    
    new_he.face = h_left.face
    new_het.face = h_right.face

    dcel.half_edges.append(new_he)
    dcel.half_edges.append(new_het)

    queue.remove_circle_event(y)

    for neighbor in (left_leaf, right_leaf):
        if neighbor.circle_event == y.circle_event:
            queue.remove_circle_event(neighbor)
            neighbor.circle_event = None

    check_circle_event(left_leaf, right_leaf, successor(right_leaf))
    check_circle_event(predecessor(left_leaf), left_leaf, right_leaf)

    return root

    if hasattr(left_leaf, "face") and left_leaf.face is not None:
        e_lr.face = left_leaf.face
    else:
        e_lr.face = getattr(e_old_left, "face", None)

    if hasattr(right_leaf, "face") and right_leaf.face is not None:
        e_rl.face = right_leaf.face
    else:
        e_rl.face = getattr(e_old_right, "face", None)

    dcel.half_edges.extend([e_lr, e_rl])



    
    
    
    
    
    
    

    