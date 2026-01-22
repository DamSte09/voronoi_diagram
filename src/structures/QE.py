from src.structures.BST import Leaf
import math

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
            print("Event wasn't removed")
            pass

        
class SiteEvent:
    def __init__(self, point):
        self.centre = point


class CircleEvent:
    def __init__(self, point: list, leaf_pointer: Leaf):
        self.centre = point
        self.leaf_pointer = leaf_pointer
        self.radius = None
        self.circle_center = None
        self.is_valid = True
        self.triple_points = None
        self.triple_arcs = None

    def is_possible(a, b, c):
        if CircleEvent.compute_circle_center(a, b, c):
            return True
        return False
    
    @staticmethod
    def compute_circle_center(a, b, c):
        det = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
        if det > 0:
            return None, None

        ax, ay = a
        bx, by = b
        cx, cy = c

        A = bx - ax
        B = by - ay
        C = cx - ax
        D = cy - ay

        E = A * (ax + bx) + B * (ay + by)
        F = C * (ax + cx) + D * (ay + cy)
        G = 2 * (A * (cy - by) - B * (cx - bx))

        if G == 0:
            return None, None

        ox = (D * E - B * F) / G
        oy = (A * F - C * E) / G
        print("Circle center:", ox, oy)
        return ox, oy

    @staticmethod
    def _calculate_angle(point, center):
        return math.atan2(point[1] - center[1], point[0]- center[0])

    @staticmethod
    def check_clockwise(a, b, c, center):
        ang_a = CircleEvent._calculate_angle(a, center)
        ang_b = CircleEvent._calculate_angle(b, center)
        ang_c = CircleEvent._calculate_angle(c, center)

        return (ang_c - ang_a) % (2 * math.pi) <= (ang_c - ang_b) % (2 * math.pi)

