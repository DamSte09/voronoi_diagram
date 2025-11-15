from src.structures.QE import EventsQueue
from src.structures.DCEL import DCEL
from src.structures.BST import Leaf, Node
from funcs import successor,predecessor, remove_from_queue

def handle_circle_event(y: Leaf, root: Node, queue: EventsQueue, dcel: DCEL):
    left_leaf = predecessor(y)
    right_leaf = successor(y)

    root.remove_leaf(y)
    queue.remove_circle_event(y)
    
    for neighbor in (left_leaf, right_leaf):
        if neighbor.circle_event == y.circle_event:
            queue.remove_circle_event(neighbor)
            neighbor.circle_event = None

    
    root.balance_tree()
    
    
    

        
        