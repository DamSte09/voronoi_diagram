
class EventsQueue:
    def __init__(self, points):
        self.points = points
        self.site_events = []
        self.circle_events = [] 
        
    def inicialize_queue(self):
        """Initialize queue by filling up with upcoming site_events and sorts them descending by y"""
        self.points.sort(key=lambda point:point[1], reverse=True)
        for point in self.points:
            self.site_events.append(SiteEvent(point))
        
    def remove_biggest_y(self):
        """Removes event with the largest y coordinate"""
        all_se = self.site_events
        all_ce = self.circle_events
        points = self.points

        biggest_se = max(all_se, key=lambda se: se.centre[1])
        print(biggest_se.centre)
        
        if all_ce != []:
            biggest_ce = max(all_ce, key=lambda ce: ce.event_point[1])
            print(biggest_ce.centre)

            if biggest_ce.centre[1] < biggest_se.centre[1]:
                all_se.remove(biggest_se.centre)    
                points.remove(biggest_se.centre)
            else:
                all_ce.remove(biggest_ce.centre)    
                points.remove(biggest_ce.centre)
        else:
            all_se.remove(biggest_se.centre)    
            points.remove(biggest_se.centre)
        
        self.site_events = all_se
        self.circle_events = all_ce
        self.points = points       

    def check_if_circle_event(self, event):
        all_se = self.site_events
        all_se.remove(event)
        

class SiteEvent:
    def __init__(self, point):
        self.centre = point


class CircleEvent:
    def __init__(self, point):
        self.event_point = point
        self.node_pointer = ""
