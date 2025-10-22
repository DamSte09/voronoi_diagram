
P = [[1,2], [ 5,2 ], [1,6], [5,1]]


# najpierw drzewo binarne

class BinarySearchTree:
    def __init__(self, node):
        self.root = None
        self.node = node
        self.list_of_nodes = []

    def is_root(self):
        if self.list_of_nodes == []:
            self.root = self.node
            self.list_of_nodes.append(self.root)


class TreeNode:
    def __init__(self, point):
        self.point = point
        self.left = None
        self.right = None



