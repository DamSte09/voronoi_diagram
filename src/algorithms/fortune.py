from src.structures.QE import EventsQueue, SiteEvent, CircleEvent
from src.structures.BST import Root
from src.structures.DCEL import DCEL
from src.algorithms.site import handle_site_event
from src.algorithms.circle import handle_circle_event


def compute_fortune(points):
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

    dcel.finish_edges(root, points)
    return dcel
