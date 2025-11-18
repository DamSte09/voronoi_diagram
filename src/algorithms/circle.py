from src.structures.QE import EventsQueue
from src.structures.DCEL import DCEL, Vertex, HalfEdge, Face
from src.structures.BST import Leaf, Node
from funcs import successor,predecessor, remove_from_queue, circle_center, check_circle_event

def handle_circle_event(y: Leaf, root: Node, queue: EventsQueue, dcel: DCEL):
    left_leaf = predecessor(y)
    right_leaf = successor(y)

    A = left_leaf.centre
    B = y.centre
    C = right_leaf.centre
    
    bp = y.parent


    # should only happen when only B vanished
    cc = circle_center(A, B, C)
    
    V_cc = Vertex(cc)
    dcel.vertices.append(V_cc)
    
    e_lr = HalfEdge()
    e_rl = HalfEdge()
    
    e_lr.twin = e_rl
    e_rl.twin = e_lr

    e_lr.origin = V_cc
    e_rl.origin = V_cc
    
    # using pointers to halfedge, attach the 3 new records
    
    # Half edge from old node
    e_old_left = bp.half_edge
    e_old_right = bp.half_edge.twin
    
    # Closing cicle on old edge
    e_lr.next = e_old_left
    e_old_left.prev = e_lr
    
    e_old_left.next = e_rl
    e_rl.prev = e_old_left

    e_rl.next = e_old_right
    e_old_right.prev = e_rl

    e_old_right.next = e_lr
    e_lr.prev = e_old_right

    if hasattr(left_leaf, "face") and left_leaf.face is not None:
        e_lr.face = left_leaf.face
    else:
        e_lr.face = getattr(e_old_left, "face", None)

    if hasattr(right_leaf, "face") and right_leaf.face is not None:
        e_rl.face = right_leaf.face
    else:
        e_rl.face = getattr(e_old_right, "face", None)

    dcel.half_edges.extend([e_lr, e_rl])

    root.replace_vanishing_leaf(y, A, C)
    root.balance_tree()

    queue.remove_circle_event(y)
    
    for neighbor in (left_leaf, right_leaf):
        if neighbor.circle_event == y.circle_event:
            queue.remove_circle_event(neighbor)
            neighbor.circle_event = None
            
            

    check_circle_event(left_leaf, right_leaf, successor(right_leaf))
    check_circle_event(predecessor(left_leaf), left_leaf, right_leaf)

    
    
    
    
    
    
    

    