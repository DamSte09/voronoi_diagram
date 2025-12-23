from src.utils.points import readPointsFromFile
from src.structures.QE import EventsQueue, SiteEvent, CircleEvent
from src.structures.BST import Root, Node, Leaf
from src.structures.DCEL import DCEL, Vertex, HalfEdge, Face
from src.algorithms.site import handle_site_event
from src.algorithms.circle import handle_circle_event

import streamlit as st


def main():
    points = readPointsFromFile("data/points.csv")

    Q = EventsQueue(points)    
    root = Root()
    dcel = DCEL()
    
    while Q.all_events:
    # for _ in range():
        event = Q.all_events.pop(0)
        print('\n\n')
        print("New event point:", event.centre)
        print("All points: ", [e.centre for e in Q.all_events])
        print('\n')
    
        if isinstance(event, SiteEvent):
            root = handle_site_event(root, event, queue=Q, dcel=dcel )
        else:
            print("Event point:", event.centre, "Event pointer: ", event.leaf_pointer)
            vanishing_leaf = event.leaf_pointer
            print(vanishing_leaf.centre)
            root = handle_circle_event(vanishing_leaf, root, Q, dcel)


        print(Q.all_events)
    print(root.show_all_leafs())
    #st.scatter_chart(points)

if __name__ == '__main__':
    main()
