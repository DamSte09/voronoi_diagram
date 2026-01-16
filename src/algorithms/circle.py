import math

from src.structures.QE import EventsQueue, CircleEvent
from src.structures.DCEL import DCEL, Vertex, HalfEdge, Face
from src.structures.BST import Leaf, Node, Root
from src.algorithms.site import check_circle_event

def handle_circle_event(
    event: CircleEvent, y_sweep: float, root: Root, queue: EventsQueue, dcel: DCEL
):
    # 1. Walidacja zdarzenia
    arc = event.leaf_pointer
    if arc is None or arc.circle_event is not event or not event.is_valid:
        return root

    # 2. Sąsiedzi
    left_arc = arc.predecessor()
    right_arc = arc.successor()

    if left_arc is None or right_arc is None:
        return root

    # 3. Tworzymy wierzchołek Voronoi
    v = Vertex(event.circle_center)
    dcel.vertices.append(v)

    # 4. Domykamy half-edge’y breakpointów (a,b) i (b,c)
    # Szukamy węzłów BST, które odpowiadają tym breakpointom
    parent = arc.parent

    # breakpoint (a, b)
    if isinstance(parent, Node):
        if parent.left_point == left_arc.centre and parent.right_point == arc.centre:
            he1 = parent.half_edge
        elif parent.left_point == arc.centre and parent.right_point == right_arc.centre:
            he1 = parent.half_edge
        else:
            he1 = None
    else:
        he1 = None

    if he1 is not None:
        he1.origin = v
        he1.twin.origin = v

    # 5. Usuwamy łuk z beachline
    root.replace_vanishing_leaf(arc, left_arc.centre, right_arc.centre)

    # 6. Nowy breakpoint (a, c) → nowa krawędź Voronoi
    he_ac = HalfEdge()
    he_ca = HalfEdge()

    he_ac.twin = he_ca
    he_ca.twin = he_ac

    he_ac.origin = v
    he_ca.origin = v

    face_a = dcel.add_face(left_arc.centre)
    face_c = dcel.add_face(right_arc.centre)

    he_ac.face = face_c
    he_ca.face = face_a

    dcel.half_edges.extend([he_ac, he_ca])

    # Nowy breakpoint MUSI trafić do odpowiedniego Node w BST
    # Szukamy lowest common ancestor left_arc i right_arc
    curr = left_arc
    while curr.parent and (
        curr.parent.left_point != left_arc.centre
        or curr.parent.right_point != right_arc.centre
    ):
        curr = curr.parent

    if isinstance(curr.parent, Node):
        curr.parent.half_edge = he_ac

    # 7. Unieważniamy stare zdarzenia kołowe
    if left_arc.circle_event:
        queue.remove_from_queue(left_arc.circle_event)
        left_arc.circle_event = None

    if right_arc.circle_event:
        queue.remove_from_queue(right_arc.circle_event)
        right_arc.circle_event = None

    # 8. Sprawdzamy nowe circle eventy
    left_left = left_arc.predecessor()
    if left_left:
        check_circle_event([left_left, left_arc, right_arc], y_sweep, queue)

    right_right = right_arc.successor()
    if right_right:
        check_circle_event([left_arc, right_arc, right_right], y_sweep, queue)

    return root
