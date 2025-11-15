from src.structures.QE import EventsQueue
from src.structures.DCEL import DCEL
from src.structures.BST import Leaf, Node

def handle_circle_event(y: Leaf, root: Node, queue: EventsQueue, dcel: DCEL):
    root.remove_leaf(y)
    root.balance_tree()
    
    

        
        