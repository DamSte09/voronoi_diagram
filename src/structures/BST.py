from __future__ import annotations

import math
import queue

class Root:
    def __init__(self, node=None):
        self.node = node

    def show_all_leafs(self):
        all_leafs = []
        curr = self.node
        while isinstance(curr, Node):
            curr = curr.left_child
        first_leaf = curr
        succ = first_leaf.successor()
        all_leafs.extend([first_leaf, succ])
        while succ is not None:
            succ = succ.successor()
            if succ is None:
                break
            all_leafs.append(succ)
        
        print("All centres from leaves: ", [leaf.centre for leaf in all_leafs])


    def height(self, node):
        if node is None or isinstance(node, Leaf):
            return 0
        return 1 + max(self.height(node.left_child), self.height(node.right_child))

    def balance_factor(self, node):
        if not isinstance(node, Node):
            return 0
        return self.height(node.left_child) - self.height(node.right_child)

    def update_node_points(self, node):
        if not isinstance(node, Node):
            return

        left = node.left_child
        while isinstance(left, Node):
            left = left.right_child
        node.left_point = left.centre

        right = node.right_child
        while isinstance(right, Node):
            right = right.left_child
        node.right_point = right.centre

    def _update_points_upwards(self, node):
        curr = node
        while curr is not None and isinstance(curr, Node):
            self.update_node_points(curr)
            curr = curr.parent

    def _fix_parents(self, node):
        if isinstance(node, Node):
            if node.left_child:
                node.left_child.parent = node
            if node.right_child:
                node.right_child.parent = node

    # ---------- ROTATIONS ----------

    def rotate_left(self, x):
        y = x.right_child
        T2 = y.left_child

        y.parent = x.parent
        if x.parent:
            if x.parent.left_child == x:
                x.parent.left_child = y
            else:
                x.parent.right_child = y

        y.left_child = x
        x.parent = y
        x.right_child = T2
        if T2:
            T2.parent = x

        self.update_node_points(x)
        self.update_node_points(y)
        return y

    def rotate_right(self, y):
        x = y.left_child
        T2 = x.right_child

        x.parent = y.parent
        if y.parent:
            if y.parent.left_child == y:
                y.parent.left_child = x
            else:
                y.parent.right_child = x

        x.right_child = y
        y.parent = x
        y.left_child = T2
        if T2:
            T2.parent = y

        self.update_node_points(y)
        self.update_node_points(x)
        return x

    # ---------- AVL ----------

    def balance_node(self, node):
        bf = self.balance_factor(node)

        if bf > 1:
            if self.balance_factor(node.left_child) < 0:
                node.left_child = self.rotate_left(node.left_child)
            return self.rotate_right(node)

        if bf < -1:
            if self.balance_factor(node.right_child) > 0:
                node.right_child = self.rotate_right(node.right_child)
            return self.rotate_left(node)

        return node

    def rebalance_upwards(self, start):
        curr = start
        while curr:
            parent = curr.parent
            new = self.balance_node(curr)
            self._fix_parents(new)

            if new.parent is None:
                self.node = new
            curr = parent

    # ---------- REMOVE LEAF (CIRCLE EVENT) ----------

    def replace_vanishing_leaf(self, leaf: Leaf):
        parent = leaf.parent
        if parent is None:
            self.node = None
            return

        sibling = parent.left_child if parent.right_child == leaf else parent.right_child
        grand = parent.parent

        if grand is None:
            sibling.parent = None
            self.node = sibling
            start = sibling
        else:
            sibling.parent = grand
            if grand.left_child == parent:
                grand.left_child = sibling
            else:
                grand.right_child = sibling
            start = grand

        leaf.parent = None
        parent.left_child = None
        parent.right_child = None
        parent.parent = None

        self._update_points_upwards(start)
        self.rebalance_upwards(start)

    def print_tree(self):
        """Czytelny wydruk struktury drzewa (Node / Leaf)"""

        def _print(node, prefix="", is_left=True):
            if node is None:
                return

            connector = "├── " if is_left else "└── "

            if isinstance(node, Leaf):
                print(prefix + connector + f"Leaf {tuple(node.centre)}")
            else:
                print(
                    prefix
                    + connector
                    + f"Node L={tuple(node.left_point)} R={tuple(node.right_point)}"
                )

                next_prefix = prefix + ("│   " if is_left else "    ")
                _print(node.left_child, next_prefix, True)
                _print(node.right_child, next_prefix, False)

        print("\nBeachline tree:")
        _print(self.node, "", False)


    def collect_leaves_inorder(node):
        leaves = []

        def dfs(n):
            if n is None:
                return
            if isinstance(n, Leaf):
                leaves.append(n)
            else:
                dfs(n.left_child)
                dfs(n.right_child)

        dfs(node)
        return leaves


class Node:
    """Break point on beachline, keeps 2 sorted centres by x,
      left defines left arc, right - right arc
      if parent is none then it is root
    """
    def __init__(self, left_point, right_point):
        self.left_point = left_point
        self.right_point = right_point
        self.parent = None 
        self.left_child = None 
        self.right_child = None
        self.half_edge = None

    def count_x_breakpoint(self,  y_sweep: float):
        """Counts x breakpoint for node of 2 points and sweepline on new centre"""
        x1, y1 = self.left_point
        x2, y2 = self.right_point

        if y1 == y2:
                return (x1 + x2) / 2
        
        a = y2 - y1
        b = 2 * (-y2 * x1 + y1 * x2 + y_sweep * x1 - y_sweep * x2)
        c = (y2 - y_sweep) * (x1**2 + y1**2 - y_sweep**2) - (y1 - y_sweep) * (
            x2**2 + y2**2 - y_sweep**2
        )

        delta = b*b - 4*a*c
        if delta < 0 or a == 0:
                return None 
        
        x1_bp = (-b+math.sqrt(delta)) / (2*a)
        x2_bp = (-b - math.sqrt(delta)) / (2 * a)

        if x1 < x2:
            return max(x1_bp, x2_bp)  # Prawy breakpoint
        else:
            return min(x1_bp, x2_bp)


class Leaf:
    """Lowest node of a tree, keeps centre which define arc"""
    def __init__(self, point: list):
        self.centre = point
        self.parent = None
        self.circle_event = None

    def predecessor(self) -> Leaf | None:
        """Finds leaf before the actual one
        
        :return: Leaf before or None if not any
        """
        curr = self

        while curr.parent and curr == curr.parent.left_child:
            curr = curr.parent

        if not curr.parent:
            return None

        curr = curr.parent.left_child

        while isinstance(curr, Node):
            curr = curr.right_child

        return curr

    def successor(self) -> "Leaf | None":
        """Finds leaf after the actual one
        
        :return: Leaf after or None if not any
        """
        curr = self

        while curr.parent and curr == curr.parent.right_child:
            curr = curr.parent

        if not curr.parent:
            return None

        curr = curr.parent.right_child

        while isinstance(curr, Node):
            curr = curr.left_child

        return curr

    @staticmethod
    def remove_leaf(leaf: Leaf, root_obj: Root):
        if leaf.parent is None:
            # Jeśli liść jest jedynym elementem w drzewie
            root_obj.node = None
            return

        parent = leaf.parent
        grandparent = parent.parent
        
        # Wybieramy "brata" usuwanego liścia (drugie dziecko rodzica)
        sibling = parent.right_child if parent.left_child == leaf else parent.left_child
        
        if grandparent is None:
            # Rodzic był korzeniem, teraz brat staje się nowym korzeniem
            root_obj.node = sibling
            sibling.parent = None
        else:
            # Podpinamy brata bezpośrednio do dziadka
            if grandparent.left_child == parent:
                grandparent.left_child = sibling
            else:
                grandparent.right_child = sibling
            sibling.parent = grandparent

        # Opcjonalne: Czyszczenie referencji dla garbage collectora
        leaf.parent = None
        parent.left_child = parent.right_child = parent.parent = None