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
    if arc is None or arc.circle_event != event or not event.is_valid:
        return root

    # 2. Sąsiedzi
    left_arc = arc.predecessor()
    right_arc = arc.successor()
    if left_arc is None or right_arc is None:
        return root

    # 3. Tworzymy wierzchołek Voronoi
    vertex = Vertex(event.circle_center)
    dcel.vertices.append(vertex)

    # 4. Zamykamy half-edge’y z BST
    # Szukamy węzłów BST odpowiadających breakpointom
    parent = arc.parent
    while parent and not isinstance(parent, Node):
        parent = parent.parent

    if parent:
        he = parent.half_edge
        if he:
            he.origin = vertex
            if he.twin:
                he.twin.origin = vertex

    # 5. Usuwamy łuk z beachline
    # left_point i right_point to centra sąsiadów
    root.replace_vanishing_leaf(arc)

    # 6.  Tworzymy nowy breakpoint (left_arc, right_arc)
    he_ac = HalfEdge()
    he_ca = HalfEdge()
    he_ac.twin = he_ca
    he_ca.twin = he_ac
    he_ac.origin = vertex
    he_ca.origin = vertex

    face_left = dcel.add_face(left_arc.centre)
    face_right = dcel.add_face(right_arc.centre)
    he_ac.face = face_right
    he_ca.face = face_left
    dcel.half_edges.extend([he_ac, he_ca])

    # Przypisujemy half-edge do odpowiedniego Node w BST
    # W BST szukamy lowest common ancestor left_arc i right_arc
    curr = left_arc
    while curr.parent and not (
        curr.parent.left_child == left_arc or curr.parent.right_child == right_arc
    ):
        curr = curr.parent
    if curr.parent and isinstance(curr.parent, Node):
        curr.parent.half_edge = he_ac

    # 7. Unieważniamy stare circle eventy sąsiadów
    for neighbor in [left_arc, right_arc]:
        if neighbor.circle_event:
            neighbor.circle_event.is_valid = False
            queue.remove_from_queue(neighbor.circle_event)
            neighbor.circle_event = None

    # 8. Sprawdzamy nowe circle eventy
    left_left = left_arc.predecessor()
    if left_left:
        check_circle_event([left_left, left_arc, right_arc], y_sweep, queue)

    right_right = right_arc.successor()
    if right_right:
        check_circle_event([left_arc, right_arc, right_right], y_sweep, queue)

    return root
