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
            self.site_events.append(SiteEvent(point))
            self.all_events.append(SiteEvent(point))
        
    def remove_biggest_y(self):
        """Removes event with the largest y coordinate"""
        # Poprawić na jedną listę wszystkich eventów
        all_se = self.site_events
        all_ce = self.circle_events

        biggest_se = max(all_se, key=lambda se: se.centre[1])
        print(biggest_se.centre)
        
        if all_ce != []:
            biggest_ce = max(all_ce, key=lambda ce: ce.event_point[1])
            print(biggest_ce.centre)

            if biggest_ce.centre[1] < biggest_se.centre[1]:
                all_se.remove(biggest_se.centre)    
                self.all_events.remove(biggest_se.centre)
            else:
                all_ce.remove(biggest_ce.centre)    
                self.all_events.remove(biggest_ce.centre)
        else:
            all_se.remove(biggest_se.centre)    
            self.all_events.remove(biggest_se.centre)
        
        self.site_events = all_se
        self.circle_events = all_ce

    def insert_event(self, event):
        i = 0
        while i < len(self.all_events):
            current = self.all_events[i]

            if event.centre[1] > current.centre[1]:
                break
            elif event.centre[1] == current.centre[1]:
                if type(event).__name__ == "SiteEvent" and type(current).__name__ == "CircleEvent":
                    break

            i += 1

        self.all_events.insert(i, event)

    def remove_from_queue(self, event):
        try:
            self.all_events.remove(event)
        except ValueError:
            pass

        
class SiteEvent:
    def __init__(self, point):
        self.centre = point


class CircleEvent:
    def __init__(self, point: list, node_pointer):
        self.centre = point
        self.node_pointer = None
