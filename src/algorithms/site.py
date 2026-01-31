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
    
    if root.node is Leaf:
        existing_leaf = root.node
        
        if existing_leaf.centre < new_event.centre:
            new_subtree = replace_with_subtree(existing_leaf, new_event.centre, dcel)
        else:
            new_subtree = replace_with_subtree(existing_leaf, new_event.centre, dcel)
            def rotate_right(node: Node) -> Node:
                """
                Performs a right rotation on a BST node.
                
                Before:        After:
                    node          left_child
                  LC     RC    LLC       node
                LLC LRC               LRC      RC
                
                :param node: The node to rotate
                :return: The new root of the subtree (left_child)
                """
                left_child = node.left_child
                
                # Perform rotation
                node.left_child = left_child.right_child
                if left_child.right_child is not None:
                    left_child.right_child.parent = node
                
                left_child.right_child = node
                left_child.parent = node.parent
                node.parent = left_child
                
                return left_child
            new_subtree = rotate_right(new_subtree)


        root.node = new_subtree
        new_subtree.parent = None
        root._update_points_upwards(new_subtree)

        print("Second met point: ", new_event.centre)
        return root
            
    # 2. Finds leaf of arc from beach line above the new point
    arc_above = Root.find_arc_above(root, new_event, y_sweep)
    print("Point representing arc above the new event: ", arc_above.centre)

    # Removes false alarm
    if arc_above.circle_event is not None:
        queue.remove_from_queue(arc_above.circle_event)
        arc_above.circle_event = None

    parent_arc_above = arc_above.parent

    # Replace leaf with arc above with new subtree
    new_subtree = replace_with_subtree(arc_above, new_event.centre, dcel)

    if parent_arc_above is None:
        root.node = new_subtree
        new_subtree.parent = None
    else:
        if parent_arc_above.left_child == arc_above:
            parent_arc_above.left_child = new_subtree
        else:
            parent_arc_above.right_child = new_subtree 

        new_subtree.parent = parent_arc_above
    root._update_points_upwards(new_subtree)

    print("Left arc of a new subtree root:", new_subtree.left_point) 
    print("Middle arc:", new_subtree.right_child.left_child.centre)
    print("Right arc:", new_subtree.right_child.right_child.centre)

    
    # dcel.add_site_halfedges(new_event.centre, new_subtree)

    # 4. step, checking circle events for new triplets
    # Finding predecessor and successor
    left_neighbour = new_subtree.left_child.predecessor()
    right_neighbour = new_subtree.right_child.right_child.successor()

    if left_neighbour:
        left_three_arcs = [
            left_neighbour,
            new_subtree.left_child,
            new_subtree.right_child.left_child,
        ]
        CircleEvent.check_circle_event(left_three_arcs, y_sweep, queue)

    if right_neighbour:
        right_three_arcs = [
            new_subtree.right_child.left_child,
            new_subtree.right_child.right_child,
            right_neighbour,
        ]
        CircleEvent.check_circle_event(right_three_arcs, y_sweep, queue)

    return root


def replace_with_subtree1(arc_above: Leaf, new_centre: list, dcel: DCEL) -> Node:
    """
    Replaces a leaf with a subtree after a site event.
    Structure:

            N(j, i)
           /      \
        L(j)     N(i, j)
                 /    \
              L(i)    L(j)
    """

    point_j = arc_above.centre
    point_i = new_centre

    # --- liście ---
    left_leaf = Leaf(point_j)
    middle_leaf = Leaf(point_i)
    right_leaf = Leaf(point_j)

    # --- root node: breakpoint (j, i) ---
    root = Node(left_point=point_j, right_point=point_i)

    root.left_child = left_leaf
    left_leaf.parent = root

    # --- right node: breakpoint (i, j) ---
    right_node = Node(left_point=point_i, right_point=point_j)

    right_node.parent = root
    root.right_child = right_node

    right_node.left_child = middle_leaf
    right_node.right_child = right_leaf

    middle_leaf.parent = right_node
    right_leaf.parent = right_node

    # --- DCEL / half-edges ---
    he_ji = HalfEdge()
    he_ij = HalfEdge()

    he_ji.twin = he_ij
    he_ij.twin = he_ji

    face_j = dcel.add_face(point_j)
    face_i = dcel.add_face(point_i)

    he_ji.face = face_i
    he_ij.face = face_j

    root.half_edge = he_ji
    right_node.half_edge = he_ij

    dcel.half_edges.extend([he_ji, he_ij])

    return root


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
    # AB = (point_j, point_i)
    # BA = (point_i, point_j)

    edge_AB = HalfEdge()
    edge_BA = HalfEdge()

    # edge_AB.origin = AB
    # edge_BA.origin = BA

    edge_AB.origin = None
    edge_BA.origin = None

    face_A = dcel.add_face(A)
    face_B = dcel.add_face(B)

    edge_AB.face = face_B
    edge_BA.face = face_A

    # face_A.outer_component = face_A.outer_component or edge_AB
    # face_B.outer_component = face_B.outer_component or edge_BA

    edge_AB.twin = edge_BA
    edge_BA.twin = edge_AB

    subtree_root.half_edge = edge_AB
    right_node.half_edge = edge_BA

    dcel.half_edges.extend([edge_AB, edge_BA])

    return subtree_root
