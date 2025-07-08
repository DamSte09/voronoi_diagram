from points import readPointsFromFile
import streamlit as st



def main():
    points = readPointsFromFile("points.csv")

    st.scatter_chart(points)
    

    

if __name__ == '__main__':
    main()
