#!/usr/bin/env python
import csv
import numpy as np
import pandas as pd


def generatePoints(number_points):
    array_points = []
    for i in range(number_points): 
        point = np.random.uniform(0, 10, size  = 2)
        array_points.append(point)
    return array_points

def savePointsToFile(array_points):
    df = pd.DataFrame(array_points)
    df.to_csv("sdf.csv", index = False, sep = ";")
    print("Zapisano do pliku")

def readPointsFromFile(path):
    array_points = []

    try:
        with open(path) as csvfile:
            reader = csv.reader(csvfile, delimiter =',', quoting=csv.QUOTE_NONNUMERIC)
            for row in reader:
                array_points.append(row)

    except Exception as e:
        print("Error: ", e)
    
    return array_points

def main():
    print("zaczynam")
    points = []
    N = 10

    # print("Punkty z pliku")
    # points = readPointsFromFile("data/points.csv") 
    # print(points)

    print("Wygenerowane punkty")
    points = generatePoints(N)
    print(points)


    savePointsToFile(points)

    
    #points = np.asarray(points)
    # plt.scatter(points[:, 0], points[:, 1])


if __name__ == '__main__':
    main()
