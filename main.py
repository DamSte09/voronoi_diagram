from src.utils.points import readPointsFromFile
from src.structures.QE import EventsQueue, SiteEvent, CircleEvent
from src.structures.BST import Root, Node, Leaf
from src.structures.DCEL import DCEL, Vertex, HalfEdge, Face
from src.algorithms.site import handle_site_event
from src.algorithms.circle import handle_circle_event

import streamlit as st
import matplotlib.pyplot as plt


def main():
    points = readPointsFromFile("data/points.csv")

    Q = EventsQueue(points)    
    root = Root()
    dcel = DCEL()
    sweepline = None
    
    while Q.all_events:
    # for _ in range():
        event = Q.all_events.pop(0)


    
        if isinstance(event, SiteEvent):
            sweepline = event.centre[1]
            print('\n')
            print("New site event point:", event.centre)
            print('\n')
            root = handle_site_event(root, event, queue=Q, dcel=dcel, y_sweep=sweepline)
        elif isinstance(event, CircleEvent) and event.is_valid:
            sweepline = event.centre[1]
            print("Circle Event point:", event.centre, "Event pointer: ", event.leaf_pointer)
            #vanishing_leaf = event.leaf_pointer
            root = handle_circle_event(event, sweepline,root, Q, dcel)
        else:
            continue

    print("DCEL vertices:", [ (v.x, v.y) for v in dcel.vertices])
    print("DCEL faces:", [f.centre for f in dcel.faces])
    print("DCEL half-edges:", len(dcel.half_edges))
    print("Total vertex count:", len(dcel.vertices))

    root.show_all_leafs()
    root.print_tree()
    fig, ax = plt.subplots()  # Create a figure containing a single Axes.
    x = []
    y=[]
    vx = []
    vy = []
    for v in dcel.vertices:
        vx.append(v.x)
        vy.append(v.y)
    ax.scatter(vx, vy, color='red')  # Plot some data on the axes.

    for point in points:
        x.append(point[0])
        y.append(point[1])
    plt.scatter(x, y)
    plt.savefig("my_voronoi_diagram.png")
    #st.scatter_chart(points)

if __name__ == '__main__':
    main()
