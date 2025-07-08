#!/usr/bin/env python
import csv
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd



def generatePoints(number_points):
    array_points = []
    for i in range(number_points): 
        point = np.random.uniform(0, 10, size  = 2)
        array_points.append(point)
    return array_points



def savePointsToFile(array_points):
    df = pd.DataFrame(array_points)
    df.to_csv("points.csv", index = False)
    print("Zapisano do pliku")



def readPointsFromFile(path):
    try:
        df = pd.read_csv(path)
        array_points = df.to_numpy()

        return array_points

    except e:
        print("Nie znaleziono pliku")




def main():
    print("zaczynam")
    points = []
    N = 10

    print("Punkty z pliku")
    points = readPointsFromFile("points.csv") 
    print(points)

    print("Wygenerowane punkty")
    points = generatePoints(N)
    print(points)


    savePointsToFile(points)

    
    points = np.asarray(points)
# plt.scatter(points[:, 0], points[:, 1])


if __name__ == '__main__':
    main()
