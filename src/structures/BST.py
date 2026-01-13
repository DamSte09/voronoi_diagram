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
    def replace_vanishing_leaf(self, leaf, left_point, right_point):
        """Removes fading leaf which represent fading arc in BST
        After leaf is removed, points in grandparent node are updated.

        :param leaf: Leaf which represnts fading arc
        """
        # parent of leaf
        leaf_parent = leaf.parent
        if leaf_parent is None:
            return

        # Find which child is sibling of a leaf
        if leaf_parent.left_child == leaf:
            replacement = leaf_parent.right_child
        else:
            replacement = leaf_parent.left_child

        grand = leaf_parent.parent

        # Is leaf_parent root
        if grand is None:
            replacement.parent = None
            self.node = replacement
        else:
            # Grandparent is now parent of replacement
            replacement.parent = grand

            # Check which child new replacement is and replaces child
            if grand.right_child == leaf_parent:
                grand.right_child = replacement
            else:
                grand.left_child = replacement

        if isinstance(replacement, Node):
            replacement.left_point = left_point
            replacement.right_point = right_point

        # Updates points in nodes
        self._update_points_upwards(replacement)

        # Cleanup
        leaf.parent = None
        leaf_parent.left_child = None
        leaf_parent.right_child = None
        leaf_parent.parent = None
        if leaf.circle_event is not None:
            # queue.remove_from_queue(leaf.circle_event)
            leaf.circle_event = None

        return self

    def _update_points_upwards(self, node):
        current = node
        while current is not None and isinstance(current, Node):
            # lewe poddrzewo: najbardziej prawy liść
            left = current.left_child
            while isinstance(left, Node):
                left = left.right_child
            current.left_point = left.centre

            # prawe poddrzewo: najbardziej lewy liść
            right = current.right_child
            while isinstance(right, Node):
                right = right.left_child
            current.right_point = right.centre

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

    