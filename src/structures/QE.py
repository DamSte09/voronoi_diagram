from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.structures.QE import Leaf
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
    def __init__(self, point: list, leaf_pointer: "Leaf"):
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
    def check_circle_event(arcs: list(), y_sweep: float, queue: EventsQueue):
        """
        Checks whether three consecutive arcs generate a valid circle event.
        If yes, inserts it into the event queue.
        """

        a, b, c = arcs
        A = a.centre
        B = b.centre
        C = c.centre

        # --- usuwamy stare zdarzenie środkowego łuku ---
        if b.circle_event is not None:
            queue.remove_from_queue(b.circle_event)
            b.circle_event = None

        # --- orientacja: MUSI być zgodna z ruchem wskazówek zegara ---
        # det < 0 → clockwise
        det = (B[0] - A[0]) * (C[1] - A[1]) - (B[1] - A[1]) * (C[0] - A[0])

        if det > 0:
            return

        # --- środek okręgu ---
        ux, uy = CircleEvent.compute_circle_center(A, B, C)
        if ux is None or uy is None:
            return

        # --- promień ---
        dx = ux - B[0]
        dy = uy - B[1]
        radius = math.hypot(dx, dy)

        # --- y zdarzenia (najniższy punkt okręgu) ---
        event_y = uy - radius

        # zdarzenie musi być poniżej sweep line
        if event_y >= y_sweep:
            return

        # --- tworzymy zdarzenie ---
        event_point = (ux, event_y)
        event = CircleEvent(point=event_point, leaf_pointer=b)
        event.circle_center = (ux, uy)
        event.radius = radius
        event.triple_arcs = (a, b, c)
        event.triple_points = (A, B, C)
        event.is_valid = True

        b.circle_event = event
        queue.insert_event(event)

