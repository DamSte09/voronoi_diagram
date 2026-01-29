from __future__ import annotations

from logging import root
import math
import queue

from src.structures.QE import SiteEvent

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

    def find_arc_above(root, event: SiteEvent, y_sweep: float):
        curr = root.node
        x = event.centre[0]

        while isinstance(curr, Node):
            xb = curr.count_x_breakpoint(y_sweep)
            print("Breakpoint x for points ", curr.left_point, curr.right_point, " at y=", y_sweep, " is ", xb)
            if xb is None:
                raise RuntimeError(
                    f"Invalid breakpoint for points "
                    f"{curr.left_point}, {curr.right_point} at y={y_sweep}"
                )

            if x < xb:
                curr = curr.left_child
            else:
                curr = curr.right_child

        return curr

    def find_breakpoint_nodes(self, leaf: Leaf):
        """
        Znajduje dwa węzły (Node), które reprezentują breakpointy 
        sąsiadujące z liściem (łukiem) w Beach Line.
        """
        left_breakpoint = None
        right_breakpoint = None

        # Idziemy w górę drzewa od liścia
        current = leaf
        while current.parent is not None:
            parent = current.parent
            
            # Jeśli przyszliśmy z prawej strony, to parent jest lewym breakpointem
            if parent.right_child == current:
                if left_breakpoint is None:
                    left_breakpoint = parent
            
            # Jeśli przyszliśmy z lewej strony, to parent jest prawym breakpointem
            if parent.left_child == current:
                if right_breakpoint is None:
                    right_breakpoint = parent
            
            # Jeśli znaleźliśmy oba, możemy przestać (opcjonalne, ale przyspiesza)
            if left_breakpoint and right_breakpoint:
                break
                
            current = parent

        return left_breakpoint, right_breakpoint

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

    def count_x_breakpoint(self, y_sweep: float):
        """
        Oblicza współrzędną x punktu przecięcia dwóch parabol.
        
        Parameters
        ----------
        y_sweep : float
            Pozycja linii zamiatającej (sweep line)
        
        Returns
        -------
        float or None
            Współrzędna x punktu przecięcia lub None jeśli nie istnieje
        """
        x1, y1 = self.left_point
        x2, y2 = self.right_point
        
        # Przypadek gdy oba punkty mają tę samą współrzędną y
        # (breakpoint jest dokładnie pośrodku)
        if y1 == y2:
            return (x1 + x2) / 2
        
        # Przypadek gdy lewy punkt jest na linii zamiatającej
        if y1 == y_sweep:
            return x1
        
        # Przypadek gdy prawy punkt jest na linii zamiatającej
        if y2 == y_sweep:
            return x2
        
        # Podstawowe współczynniki równania
        u = 2 * (y1 - y_sweep)
        v = 2 * (y2 - y_sweep)
        
        # Rozwiązanie równania kwadratowego:
        # 1/u * (x² - 2*x1*x + x1² + y1² - y_sweep²) = 1/v * (x² - 2*x2*x + x2² + y2² - y_sweep²)
        
        # Po przekształceniu do postaci: (u-v)x² + 2(x2*v - x1*u)x + ... = 0
        # zgodnie z algorytmem Wolframa Alpha użytym w foronoi:
        
        a = u - v
        
        if abs(a) < 1e-10:
            return (x1 + x2) / 2
        
        # Obliczenie pierwiastka z wzoru z foronoi
        # x = -(sqrt(v * (x1² * u - 2*x1*x2*u + y1²*(u-v) + x2²*u) + y2²*u*(v-u) + y_sweep²*(u-v)²) + x1*v - x2*u) / (u-v)
        
        term1 = x1**2 * u - 2*x1*x2*u + y1**2*(u-v) + x2**2*u
        term2 = y2**2 * u * (v-u)
        term3 = y_sweep**2 * (u-v)**2
        
        discriminant = v * term1 + term2 + term3
        
        if discriminant < 0:
            return None
        
        sqrt_term = math.sqrt(discriminant)
        x = -(sqrt_term + x1*v - x2*u) / a
        
        return x


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

    def left_breakpoint_node(self, root: Root) -> Node | None:
        """Finds left breakpoint Node in BST beachline
        
        :return: Node or None if not any
        """
        curr = self
        while curr.parent and curr == curr.parent.left_child:
            curr = curr.parent

        if not curr.parent:
            return None

        return curr.parent
    
    def right_breakpoint_node(self, root: Root) -> Node | None:
        """Finds right breakpoint Node in BST beachline
        
        :return: Node or None if not any
        """
        curr = self
        while curr.parent and curr == curr.parent.right_child:
            curr = curr.parent

        if not curr.parent:
            return None

        return curr.parent