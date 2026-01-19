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


    # TO JEST PROBLEMEM, NIE USUWA POPRAWNIE LIŚCI
    def replace_vanishing_leaf(self, leaf: Leaf):
        """
        Removes a leaf representing a disappearing arc from the beachline BST.
        Structural operation only — no geometry is handled here.
        """

        parent = leaf.parent
        if parent is None:
            # Jedyny element w drzewie
            self.node = None
            return

        # Sibling (drugie dziecko rodzica)
        if parent.left_child is leaf:
            sibling = parent.right_child
        else:
            sibling = parent.left_child

        grandparent = parent.parent

        # 1. Podpinamy sibling zamiast parent
        sibling.parent = grandparent

        if grandparent is None:
            # parent był rootem
            self.node = sibling
        else:
            if grandparent.left_child is parent:
                grandparent.left_child = sibling
            else:
                grandparent.right_child = sibling

        # 2. Czyścimy referencje (GC / debug)
        leaf.parent = None
        parent.left_child = None
        parent.right_child = None
        parent.parent = None

        # 3. Aktualizacja breakpointów w górę drzewa
        self._update_points_upwards(sibling.parent)

        return

    def _update_points_upwards(self, start):
        """
        Recomputes breakpoint-defining points (left_point, right_point)
        for all nodes on the path from `start` up to the root.
        """

        current = start

        while current is not None and isinstance(current, Node):
            # --- lewy punkt: najbardziej prawy liść w lewym poddrzewie ---
            left_sub = current.left_child
            while isinstance(left_sub, Node):
                left_sub = left_sub.right_child

            if left_sub is None:
                # struktura chwilowo niepełna — nie aktualizujemy
                pass
            else:
                current.left_point = left_sub.centre

            # --- prawy punkt: najbardziej lewy liść w prawym poddrzewie ---
            right_sub = current.right_child
            while isinstance(right_sub, Node):
                right_sub = right_sub.left_child

            if right_sub is None:
                pass
            else:
                current.right_point = right_sub.centre

            # idziemy wyżej
            current = current.parent


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