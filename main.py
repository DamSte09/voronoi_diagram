from src.utils.points import readPointsFromFile
from src.structures.QE import EventsQueue, SiteEvent, CircleEvent
from src.structures.BST import Root, Node, Leaf
from src.structures.DCEL import DCEL, Vertex, HalfEdge, Face
from src.algorithms.site import handle_site_event
#from src.algorithms.circle import handle_circle_event


import streamlit as st


def main():
    points = readPointsFromFile("data/points.csv")
    print(points)

    Q = EventsQueue(points)
    print(Q.all_events)
    
    root = Root()
    dcel = DCEL()
    
    # while Q.all_events:
    for i in range(3):
        event = Q.all_events.pop(0)

    #if isinstance(event, SiteEvent):
        root = handle_site_event(root, event, queue=Q, dcel=dcel )
    #else:
    #    handle_circle_event(event, root, Q, dcel)


    #st.scatter_chart(points)

if __name__ == '__main__':
    main()
