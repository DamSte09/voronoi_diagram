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
    vx = [v.x for v in dcel.vertices ]
    vy = [v.y for v in dcel.vertices ]
    ax.scatter(vx, vy, c="red", s=20, label="Voronoi vertices", zorder=2)

    # 3. Rysowanie punktów generatorów (blue)
    px, py = zip(*points)  # Krótszy zapis rozpakowania listy punktów
    ax.scatter(px, py, c="blue", s=40, marker="o", label="Sites", zorder=3)
    ax.set_ylim(min(py) - 1, max(py) + 1)
    ax.set_xlim(min(px) - 1, max(px) + 1)
    # Estetyka wykresu
    ax.set_aspect("equal")
    ax.set_title("Diagram Voronoi (DCEL)", fontsize=14)
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.legend(loc="upper right", frameon=True, shadow=True)

    # Dodanie marginesów
    plt.tight_layout()

    plt.savefig(filename, dpi=300)
    plt.show()
