from src.structures.BST import Leaf

class EventsQueue:
    def __init__(self, points):
        self.points = points
        self.all_events = []
        self.site_events = []
        self.circle_events = [] 
        
        for point in self.points:
            self.site_events.append(SiteEvent(point))

        self.all_events = sorted(self.site_events, key = lambda event:event.centre[1], reverse=True)
        
    def inicialize_queue(self):
        """Initialize queue by filling up with upcoming site_events and sorts them descending by y"""
        self.points.sort(key=lambda point:point[1], reverse=True)
        for point in self.points:
            self.all_events.append(SiteEvent(point))

    def insert_event(self, event):
        self.all_events.append(event)
        self.all_events.sort(key=lambda e: (e.centre[1], 1 if isinstance(e, CircleEvent) else 0))
        self.all_events.reverse() 
    
    def remove_from_queue(self, event):
        try:
            self.all_events.remove(event)
        except ValueError:
            pass

        
class SiteEvent:
    def __init__(self, point):
        self.centre = point


class CircleEvent:
    def __init__(self, point: list, leaf_pointer: Leaf):
        self.centre = point
        self.leaf_pointer = leaf_pointer
