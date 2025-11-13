from src.utils.points import readPointsFromFile
from src.structures.QE import EventsQueue, SiteEvent, CircleEvent
import streamlit as st


def main():
    points = readPointsFromFile("data/points.csv")
    print(points)
    Q = EventsQueue(points)
    Q.inicialize_queue()
    all_se = Q.site_events

    for se in all_se:
        print(se.centre)

    Q.remove_biggest_y()

    events = Q.points
    
    for event in events:
        if any(event == se.centre for se in all_se):
            print("Site event:", event)
        else:
            print("Circle event: ", event)

    #st.scatter_chart(points)

if __name__ == '__main__':
    main()
