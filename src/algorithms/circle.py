from src.structures.QE import EventsQueue
from src.structures.BST import Leaf, Node

def handle_circle_event(y: Leaf, root: Node, queue: EventsQueue):
    y.remove_leaf()
    root.balance_tree()
    

