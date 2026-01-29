import math
from src.structures.QE import EventsQueue, CircleEvent
from src.structures.DCEL import DCEL, Vertex, HalfEdge, Face
from src.structures.BST import Leaf, Node, Root


def handle_circle_event(
    event: CircleEvent, y_sweep: float, root: Root, queue: EventsQueue, dcel: DCEL
):
    # 1. Walidacja
    arc = event.leaf_pointer
    if arc is None or arc.circle_event != event or not event.is_valid:
        return root
    arc.circle_event = None

    # 2. Sąsiedzi
    left_arc = arc.predecessor()
    right_arc = arc.successor()
    if left_arc is None or right_arc is None:
        return root

    # 3. Nowy wierzchołek Voronoia
    vertex = Vertex(event.circle_center)
    dcel.vertices.append(vertex)

    # 4. Breakpointy (MUSZĄ istnieć)
    left_bp = left_arc.right_breakpoint_node(root)
    right_bp = right_arc.left_breakpoint_node(root)
    if left_bp is None or right_bp is None:
        return root

    he_left = left_bp.half_edge
    he_right = right_bp.half_edge
    if he_left is None or he_right is None:
        return root

    print("half-edge left origin:", (he_left.origin.x, he_left.origin.y) if he_left.origin else None
          , "half-edge right origin:", (he_right.origin.x, he_right.origin.y) if he_right.origin else None)
    
    # 5. Ustawiamy pochodzenie half-edgów
    he_left.origin = vertex
    he_right.origin = vertex
    vertex.incident_edge.extend([he_left, he_right])

    # 6. Nowa krawędź Voronoia
    he_new = HalfEdge()
    he_new.twin = HalfEdge()
    he_new.origin = vertex
    he_new.twin.origin = None

    # Połączenie half-edgów w cykl
    he_left.next = he_new
    he_new.next = he_right
    he_right.next = he_new.twin
    he_new.twin.next = he_left
    
    he_left.prev = he_new.twin
    he_new.prev = he_left
    he_right.prev = he_new
    he_new.twin.prev = he_right

    he_new.face = he_left.face
    he_new.twin.face = he_right.face
    vertex.incident_edge.extend([he_new, he_new.twin])
    dcel.half_edges.extend([he_new, he_new.twin])

    # 7. Aktualizacja BST
    root.replace_vanishing_leaf(arc)

    print("New half-edge origin:", (he_new.origin.x, he_new.origin.y) if he_new.origin else None)
    print("New half-edge twin origin:", (he_new.twin.origin.x, he_new.twin.origin.y) if he_new.twin.origin else None)

    if left_arc.parent.half_edge is he_left:
        left_arc.parent.half_edge = he_new
    if right_arc.parent.half_edge is he_right:
        right_arc.parent.half_edge = he_new.twin


    # 8. Unieważniamy stare circle eventy sąsiadów
    for neighbor in (left_arc, right_arc):
        if neighbor.circle_event:
            neighbor.circle_event.is_valid = False
            queue.remove_from_queue(neighbor.circle_event)
            neighbor.circle_event = None

    # 9. Sprawdzamy nowe circle eventy
    ll = left_arc.predecessor()
    if ll:
        CircleEvent.check_circle_event([ll, left_arc, right_arc], y_sweep, queue)

    rr = right_arc.successor()
    if rr:
        CircleEvent.check_circle_event([left_arc, right_arc, rr], y_sweep, queue)

    return root
