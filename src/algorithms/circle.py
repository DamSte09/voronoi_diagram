import math

from src.structures.QE import EventsQueue
from src.structures.DCEL import DCEL, Vertex, HalfEdge, Face
from src.structures.BST import Leaf, Node
from funcs import successor,predecessor, remove_from_queue, circle_center, check_circle_event

def handle_circle_event(y: Leaf, root: Node, queue: EventsQueue, dcel: DCEL):
    left_leaf = predecessor(y)
    right_leaf = successor(y)

    if left_leaf is None or right_leaf is None:
        return root
    
    A = left_leaf.centre
    B = y.centre
    C = right_leaf.centre
    
    print(f"A: {A}, B: {B}, C:{C}")

    # should only happen when only B vanished
    cc = circle_center(A, B, C)
    print("Center of a circle: ", cc)

    if cc is None or any(math.isinf(c) or math.isnan(c) for c in cc):
        print("Circle center does not exist")
        return root
    
    ux, uy = cc
    r = math.dist(cc, B) 
    if not math.isfinite(r) or r <= 0:
        return root
    y_sweep = uy - r
    
    left_bp = left_leaf.parent
    right_bp = right_leaf.parent
    if left_bp is None or right_bp is None:
        return root

    h_left = getattr(left_bp, "half_edge", None)
    h_right = getattr(right_bp, "half_edge", None)
    if h_left is None or h_right is None:
        return root

    V_cc = Vertex(cc)
    dcel.vertices.append(V_cc)

    for neighbor in (left_leaf, right_leaf):
        ev = getattr(neighbor, "circle_event", None)
        if ev is not None and ev is y.circle_event:
            queue.remove_from_queue(neighbor)
            neighbor.circle_event = None

    root.replace_vanishing_leaf(y, A, C)

    new_he = HalfEdge()
    new_het = HalfEdge()
    new_he.twin = new_het
    new_het.twin = new_he

    new_he.origin = V_cc
    h_right = V_cc

    h_left.next = new_he
    new_he.prev = h_left

    new_het.next = h_right
    h_right.prev = new_het

    new_het.prev = None

    if hasattr(h_left, "face"):
        new_he.face = h_left.face
    if hasattr(h_right, "face"):
        new_het.face = h_right.face

    dcel.half_edges.append(new_he)
    dcel.half_edges.append(new_het)

    for neighbor in (left_leaf, right_leaf):
        if getattr(neighbor, "circle_event", None) is not None:
            queue.remove_from_queue(neighbor)
            neighbor.circle_event = None

    print("od lewej do prawej")
    right_n = successor(right_leaf)
    left_n = predecessor(left_leaf)
    if right_n is not None:
        check_circle_event([left_leaf, right_leaf, right_n], y_sweep, queue)
    if left_n is not None:
        check_circle_event([left_n, left_leaf, right_leaf], y_sweep, queue)

    return root


    
    
    
    
    
    
    

    