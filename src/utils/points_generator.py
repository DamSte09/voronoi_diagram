#!/usr/bin/env python
import csv
import numpy as np
import pandas as pd


def generate_points(number_points):
    array_points = []
    for i in range(number_points): 
        point = np.random.uniform(0, 10, size  = 2)
        array_points.append(point)
    return array_points

def save_points_to_file(array_points):
    df = pd.DataFrame(array_points)
    df.to_csv("sdf.csv", index = False, sep = ";")
    print("Zapisano do pliku")

def read_points_from_file(path, sep = ';'):
    array_points = []

    try:
        with open(path) as csvfile:
            reader = csv.reader(csvfile, delimiter =sep, quoting=csv.QUOTE_NONNUMERIC)
            for row in reader:
                array_points.append(row)

    except Exception as e:
        print("Error: ", e)
    
    return array_points

def main():
    print("zaczynam")
    points = []
    N = 10

    print("Wygenerowane punkty:")
    points = generate_points(N)
    print(points)

    save_points_to_file(points)

if __name__ == '__main__':
    main()
