from src.utils.points import readPointsFromFile
from src.structures.QE import EventsQueue, SiteEvent, CircleEvent
from src.structures.BST import Root, Node, Leaf
from src.structures.DCEL import DCEL, Vertex, HalfEdge, Face
from src.algorithms.site import handle_site_event, count_x_breakpoint
from src.algorithms.circle import handle_circle_event


import streamlit as st

def collect_breakpoints(node, y_sweep, breakpoints=None):
    """Zbiera wszystkie x breakpointy w drzewie dla danego y_sweep."""
    if breakpoints is None:
        breakpoints = []

    if isinstance(node, Node):
        try:
            xb = count_x_breakpoint(node.left_point, node.right_point, y_sweep)
        except Exception:
            xb = None

        breakpoints.append(
            {
                "x_breakpoint": xb,
                "left_point": node.left_point,
                "right_point": node.right_point,
            }
        )

        # Rekurencyjnie w lewo i w prawo
        collect_breakpoints(node.left_child, y_sweep, breakpoints)
        collect_breakpoints(node.right_child, y_sweep, breakpoints)

    return breakpoints



def main():
    points = readPointsFromFile("data/points.csv")
    print(points)

    Q = EventsQueue(points)
    print(Q.all_events)
    
    root = Root()
    dcel = DCEL()
    
    # while Q.all_events:
    for _ in range(5):
        event = Q.all_events.pop(0)
        print('\n\n')
        print("New event point:", event.centre)

        if isinstance(event, SiteEvent):
            root = handle_site_event(root, event, queue=Q, dcel=dcel )
        else:
            print(event.centre, event.leaf_pointer)
            vanishing_leaf = event.leaf_pointer
            print(vanishing_leaf.centre)
            root = handle_circle_event(vanishing_leaf, root, Q, dcel)
            # problem z powtarzającymi się liściami
            print(root.show_all_leafs())

        print(Q.all_events)
    # Przykładowe użycie na końcu algorytmu:
    y_sweep = 0  # lub minimalne y w obszarze, żeby uzyskać "dolną krawędź" drzewa
    bps = collect_breakpoints(root.node, y_sweep)

    print("Breakpoints w całym drzewie po zakończeniu algorytmu:")
    for b in bps:
        print(
            f"x_breakpoint: {b['x_breakpoint']}, left: {b['left_point']}, right: {b['right_point']}"
        )
    #st.scatter_chart(points)

if __name__ == '__main__':
    main()
