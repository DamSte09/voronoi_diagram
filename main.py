from src.utils.points import readPointsFromFile
from src.structures.QE import EventsQueue, SiteEvent, CircleEvent
from src.structures.BST import Root, Node, Leaf
from src.structures.DCEL import DCEL, Vertex, HalfEdge, Face
from src.algorithms.site import handle_site_event
from src.algorithms.circle import handle_circle_event

import streamlit as st
import matplotlib.pyplot as plt

def plot_voronoi(points, dcel, filename="my_voronoi_diagram.png"):
    fig, ax = plt.subplots(figsize=(10, 10))

    # 1. Rysowanie krawędzi (używamy zbioru, aby nie rysować dwa razy tej samej linii)
    seen_edges = set()
    for he in dcel.half_edges:
        if he.origin and he.twin and he.twin.origin:
            # Tworzymy unikalny identyfikator krawędzi niezależny od kierunku
            edge_id = tuple(sorted([id(he), id(he.twin)]))
            if edge_id not in seen_edges:
                x_vals = [he.origin.x, he.twin.origin.x]
                y_vals = [he.origin.y, he.twin.origin.y]
                ax.plot(x_vals, y_vals, color="forestgreen", linewidth=1.5, zorder=1)
                seen_edges.add(edge_id)



    # 2. Rysowanie wierzchołków Voronoi (red)
    vx = [v.x for v in dcel.vertices]
    vy = [v.y for v in dcel.vertices]
    ax.scatter(vx, vy, c="red", s=20, label="Voronoi vertices", zorder=2)

    # 3. Rysowanie punktów generatorów (blue)
    px, py = zip(*points)  # Krótszy zapis rozpakowania listy punktów
    ax.scatter(px, py, c="blue", s=40, marker="o", label="Sites", zorder=3)

    # Estetyka wykresu
    ax.set_aspect("equal")
    ax.set_title("Diagram Voronoi (DCEL)", fontsize=14)
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.legend(loc="upper right", frameon=True, shadow=True)

    # Dodanie marginesów
    plt.tight_layout()

    plt.savefig(filename, dpi=300)
    plt.show()

def main():
    points = readPointsFromFile("data/points.csv")

    Q = EventsQueue(points)    
    root = Root()
    dcel = DCEL()
    sweepline = None
    
    while Q.all_events:
        event = Q.all_events.pop(0)

        print('\n')
        print("New event point:", event.centre)
        print('\n')
    
        if isinstance(event, SiteEvent):
            sweepline = event.centre[1]
            root = handle_site_event(root, event, queue=Q, dcel=dcel, y_sweep=sweepline)
        elif isinstance(event, CircleEvent) and event.is_valid:
            sweepline = event.centre[1]
            print("Event point:", event.centre, "Event pointer: ", event.leaf_pointer)
            #vanishing_leaf = event.leaf_pointer
            root = handle_circle_event(event, sweepline,root, Q, dcel)
        else:
            continue

    print("DCEL vertices:", [ (v.x, v.y) for v in dcel.vertices])
    print("DCEL faces:", [f.centre for f in dcel.faces])
    # print("DCEL half-edges:", [ (he.origin.x, he.origin.y) for he in dcel.half_edges if he.origin is not None])
    # print("Non closed half-edges:", [ (he.origin, he.twin.origin) for he in dcel.half_edges if he.twin.origin is None])
    print("Count of faces:", len(dcel.faces))
    print("Count of half-edges:", len(dcel.half_edges))
    print("Count of edges:", len(dcel.half_edges) // 2)

    print("Count of vertices:", len(dcel.vertices))

    print("Connected half-edges:")
    for he in dcel.half_edges:
        if he.origin and he.twin and he.twin.origin:
            print(f"  ({he.origin.x}, {he.origin.y}) -> ({he.twin.origin.x}, {he.twin.origin.y})")

    print("Disconnected half-edges:")
    for he in dcel.half_edges:
        if he.origin and not he.twin:
            print(f"  ({he.origin.x}, {he.origin.y}) -> (None)")

    fig, ax = plt.subplots()  # Create a figure containing a single Axes.
    x = []
    y=[]
    vx = []
    vy = []
    for point in points:
        x.append(point[0])
        y.append(point[1])
    for v in dcel.vertices:
        vx.append(v.x)
        vy.append(v.y)
    plt.scatter(x, y)
    plt.scatter(vx, vy, c='red')
    plt.savefig("my_voronoi_diagram.png")
    #st.scatter_chart(points)
    plot_voronoi(points, dcel)

if __name__ == '__main__':
    main()
