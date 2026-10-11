from src.structures.QE import EventsQueue, CircleEvent
from src.structures.DCEL import DCEL, Vertex, HalfEdge
from src.structures.BST import Root


def handle_circle_event(
    event: CircleEvent, y_sweep: float, root: Root, queue: EventsQueue, dcel: DCEL
):
    # 1. Walidacja
    arc = event.leaf_pointer
    if arc is None or arc.circle_event is not event or not event.is_valid:
        return root
    arc.circle_event = None

    # 2. Sąsiedzi
    left_arc = arc.predecessor()
    right_arc = arc.successor()
    if left_arc is None or right_arc is None:
        raise RuntimeError("Circle event for - wrong beach line")

    # 4. Breakpointy (MUSZĄ istnieć)
    left_bp = left_arc.right_breakpoint_node(root)
    right_bp = right_arc.left_breakpoint_node(root)
    if left_bp is None or right_bp is None:
        raise RuntimeError("Lack of breakpoint")
    if left_bp.half_edge is None or right_bp.half_edge is None:
        raise RuntimeError("Breakpoint without halfedge")

    # 4. Nowy wierzchołek Voronoia
    vertex = Vertex(event.circle_center)
    dcel.vertices.append(vertex)
    
    # 5. Ustawiamy pochodzenie half-edgów
    left_bp.half_edge.origin = vertex
    right_bp.half_edge.origin = vertex

    # 6. Nowa krawędź Voronoia
    he_new = HalfEdge()
    he_twin = HalfEdge()
    he_new.twin = he_twin
    he_twin.twin = he_new
    he_new.origin = vertex

    he_new.face = dcel.add_face(right_arc.centre)
    he_twin.face = dcel.add_face(left_arc.centre)

    vertex.incident_edge.extend([left_bp.half_edge, right_bp.half_edge, he_new])
    dcel.half_edges.extend([he_new, he_twin])

    surviving = right_bp if arc.parent is left_bp else left_bp
    surviving.half_edge = he_twin

    # 7. Aktualizacja BST
    root.replace_vanishing_leaf(arc)

    print("New half-edge origin:", (he_new.origin.x, he_new.origin.y) if he_new.origin else None)
    print("New half-edge twin origin:", (he_new.twin.origin.x, he_new.twin.origin.y) if he_new.twin.origin else None)

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
