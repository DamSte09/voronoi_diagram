from src.utils.points import readPointsFromFile
from src.structures.QE import EventsQueue, SiteEvent, CircleEvent
from src.structures.BST import Root, Node, Leaf
from src.structures.DCEL import DCEL, Vertex, HalfEdge, Face
from src.algorithms.site import handle_site_event
from src.algorithms.circle import handle_circle_event


import streamlit as st


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

    #st.scatter_chart(points)

if __name__ == '__main__':
    main()
