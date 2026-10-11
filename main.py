from src.utils.points_generator import read_points_from_file
from src.visualization.plotting import plot_voronoi
from src.algorithms.fortune import compute_fortune

import matplotlib.pyplot as plt


def main():
    points = read_points_from_file("sdf.csv")

    dcel = compute_fortune(points)

    print("Count of faces:", len(dcel.faces))
    print("Count of half-edges:", len(dcel.half_edges))
    print("Count of vertices:", len(dcel.vertices))

    plot_voronoi(points, dcel)


if __name__ == '__main__':
    main()
