"""Modular decomposition.

This module implements an algorithm and all required data structures for computing the modular decomposition
of an undirected graph. The algorithm was developed by Marc Tedder, Derek Corneil, Michel Habib and Christophe Paul.
However, this implementation is heavily based on the presentation of the algorithm in 'Applications of Lexicographic
Breadth-First Search to Modular Decomposition, Split Decomposition, and Circle Graphs' by Marc Tedder
(2011, pages 33-62).
"""

from collections import namedtuple
from enum import Enum, auto
from itertools import groupby
from sys import setrecursionlimit

setrecursionlimit(10 ** 6)


class Label(Enum):
    """An enum for the labels, that are used by the algorithm during 'tree_refinement()' and 'factorize()'."""
    DEAD = auto()
    ZOMBIE = auto()


class Type(Enum):
    """An enum for the type of a node (module) in a tree."""
    SERIES = auto()
    PARALLEL = auto()
    PRIME = auto()
    NODE = auto()  # A leaf


class Connectivity(Enum):
    """An enum that is used by 'label_by_component()'."""
    COMPONENT = auto()
    CO_COMPONENT = auto()


class Node:
    """A class used to represent a node in a graph.

    Attributes:
            id: A string that represents the id of a node.
            adjacent: The set of nodes that are adjacent to a node.
            alpha: A subset of nodes that are adjacent to a node.
                Nodes contained in the node's alpha set, are those that are adjacent to this node, but that are
                contained in a different tree.
    """

    def __init__(self, node_id):
        """Initialises a 'Node' object.

        Args:
            node_id: A string that holds the id of a node.
        """

        self.id = node_id
        self.adjacent = set()
        self.alpha = set()  # the active list of a node
        self.active_alpha = set()  # a subset of the active list of a node containing only the neighbors within a tree partition
        self.container = None

    def __str__(self):
        """The string method of a 'Node' object.

        Returns:
            The string representing the id of a node.
        """

        return str(self.id)

    __repr__ = __str__

    def add_neighbor(self, neighbor):
        """A method that adds a neighbored node to a node's adjacency set.

        Args:
            neighbor: The node that is added to a node's adjacency set.
        """

        self.adjacent.add(neighbor)

    def closed_neighborhood(self):
        """A method that returns the closed neighborhood of a node.

        Returns:
            The closed neighborhood of a node."""

        return {*self.adjacent, self}

    def add_alpha_neighbor(self, alpha_neighbor):
        """A method that adds a node to the node's alpha set.

        Args:
            alpha_neighbor: The node that is added to a node's alpha set.
        """

        self.alpha.add(alpha_neighbor)


class Graph:
    """A class used to represent a graph.

    Attributes:
        nodes: A dictionary that is used to represent the actual graph.
            Keys are strings that represent the id of a node.
            Values are the corresponding node objects.
    """

    def __init__(self):
        """Initialises a graph as an empty dictionary."""
        self.nodes = {}

    def add_node(self, node):
        """A method that adds a node to the graph unless it is already part of the graph.

        Args:
            node: The node that is added to the graph.
        """

        if node.id not in self.nodes.keys():
            self.nodes[node.id] = node

    def add_edge(self, u_id, v_id):
        """A method that adds an edge between two nodes to the graph.

        If either node is not already in the graph, a new node object is created and added to the graph's dictionary.
        Then the nodes are added to each other as neighbors.

        Args:
            u_id: The string representing the id of the first node.
            v_id: The string representing the id of the second node.
        """

        if u_id not in self.nodes.keys():
            self.add_node(Node(u_id))
        if v_id not in self.nodes.keys():
            self.add_node(Node(v_id))

        self.nodes[u_id].add_neighbor(self.nodes[v_id])
        self.nodes[v_id].add_neighbor(self.nodes[u_id])

    def get_nodes(self):
        """A method that returns the set of nodes of the graph."""
        return set(self.nodes.values())

    def remove_node(self, node_id):
        """A method that removes a node from the graph.

        Args:
                node_id: The string representing the id of the node that is removed from the graph.
        """

        for id, node in self.nodes.items():
            if id != node_id:
                for neighbor in list(node.adjacent):
                    if neighbor.id == node_id:
                        node.adjacent.remove(neighbor)
        del self.nodes[node_id]


class Tree:
    """A class used to represent a modular decomposition tree.

    A Tree object describes a single node in a tree. Complex trees are composed of multiple Tree objects.

    Note:
        A single Tree object is referred to as a tree node, a complex tree is referred to as a tree.
        In the case of a tree node being a leaf, the tree node represents a simple node (as like in a graph).
        When a tree node is an inner node, it represents a module.

    Attributes:
        node: The data field of a tree node. The default value 'None' is used, when the tree node is a inner node
            and therefore represents a module. When the tree node is a leaf, typically a Node object is
            contained in here.
        type: The type field of a tree node. It indicates whether a tree node refers to a module (PRIME, PARALLEL,
            SERIES) or to a simple node (NODE).
        parent: The tree node that is the parent to a tree node. If a tree node corresponds to the root of a
            complex tree, the default value 'None' is used.
        children: A list that holds the tree nodes, that are children to a tree node.

        is_marked: A flag, that is required during the refinement phase of the algorithm.
            (See 'tree_refinement()' for details.)
        label: Tree nodes are assigned labels during the execution of tree_refinement and factorize().
            The label can take on the values DEAD or ZOMBIE. Both indicate, that a tree_node is going to be split up.
            When no splitting occurs, the default value is 'None' is used. (See 'tree_refinement()' and 'factorize()'
            for details.)
        connectivity: A tuple consisting of a (co-)component-index and a (co-)component-type required to identify the
            pivot factorizing permutation. (See 'conquer_md_tree()' and 'label_by_component()' for details.)
        mu: A positive integer value used during the construction phase of the algorithm.
            (See 'build_spine()' and 'conquer_md_tree(') for details.)
        rho: A positive integer value used during the construction phase of the algorithm.
            (See 'build_spine()' and 'conquer_md_tree()' for details.)
        mark_count: A positive integer value used during 'tree_refinement()'.
        tree_index: A positive integer value used during 'tree_refinement()'.
    """

    def __init__(self, node_type, node=None):
        """Initialises a tree node.

        Args:
            node_type: The type of a node. A node can be initialised as either a 'SERIES', 'PARALLEL', 'PRIME'
                or 'NODE' node. In the latter case, the tree node is a leaf and holds a Node object.
                In all other cases the node refers to a module.
            node: The 'Node' object, which is encapsulated in the tree node. Nodes corresponding to modules have 'node'
                set to 'None'.
        """

        # Essential attributes
        self.node = node
        self.type = node_type
        self.parent = None
        self.children = []

        # Additional attributes required by the algorithm
        self.is_marked = False
        self.label = None
        self.connectivity = (None, None)  # (component_index, component_type)
        self.mu = None
        self.rho = None
        self.mark_count = 0
        self.tree_index = None

    def __iter__(self):
        """A generator that yields all nodes of the tree rooted in 'self' in a depth first manner.

        Yields:
            The next tree node.
        """

        yield self
        for child in self.children:
            yield from child

    def ancestors(self):
        """A generator that yields all ancestors of 'self' in a bottom up manner.

        Yields:
            The next tree node, which is the parent to the last yielded node.
        """

        if self.parent is not None:
            yield self.parent
            yield from self.parent.ancestors()

    def leaves(self):
        """A generator that yields all leaves of the tree rooted in 'self' starting at the left, going to the right.

        Yields:
            The next tree node, which is a leaf.
        """

        for t_node in self:
            if t_node.type is Type.NODE:
                yield t_node

    def label_by_component(self, connectivity, number_of_components=0):
        """A method that identifies the (co-)components of a tree and then labels the nodes contained in them
        according to their membership.

        (Co-)Components are either defined by the roots of a tree or by the nodes at depth-1.
        If components are to be identified and the root is 'PARALLEL' or co-components are to be identified and
        the root is 'SERIES', then the (co-)components are defined by the leaf-sets of the nodes at depth-1.
        In all other cases the leaves of the root define one (co-)component.

        The label that each node gets assigned is a tuple consisting of the number of the (co-)component and the type.

        Args:
            connectivity: Takes on the values 'COMPONENT' or 'CO_COMPONENT'.
                It indicates whether to identify components or co-components and is also used for labelling the nodes.
            number_of_components: The number of (co-)components found in earlier calls of this function. It is used to
                label the nodes.

        Returns:
            The number of (co-)components found during the execution of the method.
        """

        if self.type is Type.PARALLEL and connectivity is Connectivity.COMPONENT \
                or self.type is Type.SERIES and connectivity is Connectivity.CO_COMPONENT:
            # Multiple (co-)components defined by children of root
            for child in self.children:
                for leaf in child.leaves():
                    leaf.connectivity = (number_of_components, connectivity)
                number_of_components += 1  # Respectively number of co-components
            return number_of_components

        # Only one (co-)component defined by root
        for leaf in self.leaves():
            leaf.connectivity = (number_of_components, connectivity)
        return number_of_components + 1

    def nodes_by_label(self, label):
        """A method that returns a generator expression, which yields all nodes of a tree with a certain label.

        Args:
            label: All nodes that carry that label, should be returned.
        Returns:
            A generator expression, which yields all nodes of a tree with a certain label
        """

        return (t_node for t_node in self if t_node.label is label)

    def replace_children(self, children):
        """A method that replaces the children of 'self' in 'children', with a new node inheriting 'self''s type,
        whose children are those nodes in 'children'. It then returns this newly created node.

        Args:
            children: A list of nodes that should be removed from 'self''s children, and that should be made children
                of the new node.

        Return:
            The newly created node.
        """

        new_node = Tree(self.type)
        new_node.tree_index = children[0].tree_index  # Set the tree index as required by 'tree_refinement()'

        for child in children:
            new_node.insert(child)
            self.children.remove(child)
        self.insert(new_node)
        return new_node

    def is_degenerate(self):
        """A method that checks, whether a node is degenerate.

        Returns: 'True' if the node is degenerate. 'False' if it is not.
        """

        return self.type is Type.PARALLEL or self.type is Type.SERIES

    def unmarked_nodes(self):
        """A method, that returns a generator expression which yields all unmarked nodes of a tree.

        Returns:
            A generator expression which yields all unmarked nodes of a tree.
        """

        return (t_node for t_node in self if not t_node.is_marked)

    def group_children(self, group_fn):
        """A method, that divides the children of a node into two groups.

        Args:
            group_fn: A function, that is called on a node. It returns a boolean.
        Returns:
            A 2-tuple of lists. The first list contains all children of a node for which 'group_fn' returned 'True',
            the second list contains all children of a node for which 'group_fn' returned 'False'.
        """

        hit_group, miss_group = [], []
        for child in self.children:
            if group_fn(child):
                hit_group.append(child)
            else:
                miss_group.append(child)
        return hit_group, miss_group

    def insert(self, child):
        """A method that inserts a node as a child to 'self'.

         Args:
             child: The node that inserted a child to 'self'
        """

        self.children.append(child)
        child.parent = self

    def __str__(self):
        """The string method of a tree node.

        Returns:
            A string representation of a tree node.
        """

        return str(self.node)

    __repr__ = __str__

    def get_root(self):
        """A method, that returns the root of the tree that 'self' is contained in.

        Returns:
            The root of the tree that 'self' is contained in:
        """

        if self.parent is not None:
            return self.parent.get_root()
        return self


class PartitionClass:
    """A class that is used to represent a class within a ordered partition.

    Attributes:
        nodes: A set, that holds the nodes that belong to the partition class.
        previous: The class that is before the partition class. The default value is 'None'.
        next: The class that is after the partition class. The default value is 'None'.
    """

    def __init__(self, nodes):
        """Initialises a partition class.

        Args:
            nodes: A set, that holds the nodes that belong to the partition class.
        """

        self.nodes = nodes
        self.previous = None
        self.next = None

        # TODO: Required by 'partition_refinement()'. See 'divide_md_tree()'.
        # for n in nodes:
        #     n.container = self
        # self.has_split = False


class Partition:
    """A class used to represent a ordered partition.

    Attributes:
        head: The first class in the ordered partition.
    """

    def __init__(self):
        """Initialises a partition."""
        self.head = None

    def __iter__(self):
        """A generator, that yields the classes which form the partition.

        Yields:
            The next class in the partition.
        """

        current_p_class = self.head
        while current_p_class is not None:
            yield current_p_class
            current_p_class = current_p_class.next

    def prepend(self, p_class):
        """A method, that prepends a class to a partition.

        Args:
            p_class: The partition class which is prepended to the partition.
        """

        if self.head is not None:
            p_class.next = self.head
            self.head.previous = p_class
        self.head = p_class

    def get_first(self):
        """A method, that returns the first partition class in the partition.

        Returns:
            The first partition class in the partition.
        """

        return self.head

    def pop_first(self):
        """A method, that removes the first partition class from the partition and returns it.

        Returns:
            The first partition class in the partition. If the partition is empty, 'None' is returned.
        """

        if self.head is None:
            return None

        old_head = self.head
        if self.head.next is not None:
            self.head.next.previous = None
            self.head = self.head.next
            old_head.next = None
            return old_head

        self.head = None
        return old_head

    def replace(self, old_p_class, p_class_a, p_class_b):
        """A method that replaces a partition class with two other partition classes.

        'p_class_a' goes before 'p_class_b'. Together (under union) they represent a refinement of the old class.

        Args:
            old_p_class: A class which is going to be replaced with two classes.
            p_class_a: One of two classes, that replace the old class. This class goes directly before 'p_class_b'.
            p_class_b: The other class replacing the old class. It directly follows 'p_class_a'.
        """
        p_class_a.next = p_class_b
        p_class_b.previous = p_class_a
        if old_p_class.previous is None:
            self.head = p_class_a
        else:
            old_p_class.previous.next = p_class_a
            p_class_a.previous = old_p_class.previous
        if old_p_class.next is not None:
            old_p_class.next.previous = p_class_b
            p_class_b.next = old_p_class.next

    def flatten(self):
        """A method, that returns a set containing all nodes, contained within the partition.

        Returns:
            A set containing all nodes, contained within the partition.
        """

        return set(node for p_class in self for node in p_class.nodes)

    def is_empty(self):
        """A method used to indicated whether the partition is empty.

        Returns:
            'True' if the partition is empty, 'False' if the partition is not empty.
        """

        return self.head is None


def partition_refinement(partition, pivot_set):
    """A function that refines a partition by a pivot set.

    Args:
        partition: A partition which is to be refined.
        pivot_set:  A set which refines the partition.
    """

    # Keep track of the refined partition classes
    split_classes = []

    for x in pivot_set:
        # The class in which a element of the pivot set resides
        old_class = x.container

        if not x.container.has_split:
            # If the class has not been refined by any other element before,
            # then make new class ('split_class') containing the element and put it
            # before the refined class
            old_class.nodes.remove(x)
            old_class.has_split = True
            split_classes.append(old_class)
            split_class = PartitionClass({x})

            # Set the pointers
            if old_class == partition.head:
                partition.head = split_class
            else:
                old_class.previous.next = split_class

            split_class.previous = old_class.previous
            old_class.previous = split_class
            split_class.next = old_class

        else:
            # Else just remove the node from the class and put it in the split class
            old_class.nodes.remove(x)
            old_class.previous.nodes.add(x)
            x.container = x.container.previous

        # Remove the old class from the partition if it is empty after refinement
        if len(old_class.nodes) == 0:
            old_class.previous.next = old_class.next
            if old_class.next is not None:
                old_class.next.previous = old_class.previous

    # Delete the information about splits
    for c in split_classes:
        c.has_split = False


def md_tree(graph):
    """A function, that calculates the modular decomposition tree of a graph.

    Args:
        graph: A graph for which to calculate it's modular decomposition tree.

    Returns:
        tree: The modular decomposition tree.
    """

    (tree, partition) = divide_md_tree(graph.get_nodes(), Partition())

    return tree


def divide_md_tree(s, p):
    """A function that recursively computes the modular decomposition tree of a graph.

    The problem of computing the modular decomposition tree of graph G is solved by dividing the problem into
    sub-problems, respectively computing the modular decomposition trees for sub-graphs. When these sub-problems are
    solved, their solutions are combined to build the modular decomposition tree for the complete graph.
    The solutions to the sub-problems on their part, are obtained in the same recursive manner.

    Formally, the function computes an ordered maximal slice partition of a graph G with respect to an lexicographic
    breadth first search starting from some pivot node x. These maximal slices represent the sub-problems,
    which need to be solved recursively in order to compute the modular decomposition tree for a graph.
    For this purpose, the algorithm starts by selecting an arbitrary node x ∈ S as a pivot.
    According to this node x, the set S is split up (refined) into N(x) and V(G) - N[x].
    The set N(x) already represents maximal slice. Both sets are prepended to the initially empty partition.

    During a loop, the algorithm proceeds with removing the particular first class from the partition. Using this class
    and the leftover partition as an argument for the next call, the modular decomposition tree for the class's induced
    sub-graph in G is computed. For this purpose a new pivot is chosen, which again, refines its own class, but also all
    other partition classes in the same way according to its neighborhood.

    When the loop has finished, the modular decomposition trees for the graphs defined by the maximal slices in a
    lexicographic breath first search starting from the pivot node x have been computed.
    These are then combined to form the modular decomposition tree for the graph G.

    Args:
        s: A 'set', representing a non-empty set S ⊆ V(G), for some graph G. When the function is called for the first
            time the set S contains all of G's nodes (S = V(G)).
        p: A 'Partition', representing an ordered partition P of a non-empty set S' ⊆ V(G), where S ∩ S'= ∅.

    Returns:
        A tuple (T,P'), where T  is the modular decomposition tree for G[S], and P' = P0',...,Pk' is a refinement
        of P such that:
        1. each vertex x will have had its active list α(x) computed
        2. every vertex in S is either universal to or isolated from every Pi'
        3. for every pair Pi', Pj', i < j, such that Pi' ∪ Pj' ⊆ P for some P ∈ Partition, there is a vertex in S
           that is universal to Pi' and isolated from Pj'.
    """

    # Choose some pivot x ∈ S
    x = next(iter(s))

    # Add x to α(y), for each y ∈ N(x) ∩ (S ∪ S')
    s_ = p.flatten()  # S'
    for y in x.adjacent & (s | s_):
        y.add_alpha_neighbor(x)

    # # Refine each partition class according to the neighborhood of x
    for p_class in p:

        # A ← P ∩ N(x)
        a = p_class.nodes & x.adjacent

        # B ← P − A
        b = p_class.nodes - a

        # If A, B ≠ ∅ then replace P in P with A, B in this order
        if len(a) != 0 and len(b) != 0:
            p.replace(p_class, PartitionClass(a), PartitionClass(b))

    # # TODO: Use this for proper partition refinement instead (practically slower). See 'PartitionClass'.
    # if not p.is_empty():
    #     partition_refinement(p, x.adjacent & s_)

    # If S = {x} then return (x, P)
    if len(s) == 1 and x in s:
        tree_x = Tree(Type.NODE, x)
        x.container = tree_x
        return tree_x, p

    # If S − (N[x] ∩ S) ≠ ∅ then prepend S −(N[x] ∩ S) to P
    if not len(s - (x.closed_neighborhood() & s)) == 0:
        p.prepend(PartitionClass(s - (x.closed_neighborhood() & s)))

    # If N(x) ≠ ∅ then prepend N(x) ∩ S to P
    if not len(x.adjacent & s) == 0:
        p.prepend(PartitionClass(x.adjacent & s))

    # Initialise the ordered list of trees with {x}
    tree_x = Tree(Type.NODE, x)
    x.container = tree_x
    trees = [tree_x]

    # While P ⊆ S, where P is the first class in Partition
    while not (p.is_empty()) and p.get_first().nodes <= s:
        # Remove P from the Partition
        # (T,P) ← DivideMDTree(P,Partition)
        tree, p = divide_md_tree(p.pop_first().nodes, p)

        # Append T to the list of trees
        trees.append(tree)

    # Build the modular decomposition from the trees in the tree partition
    trees = conquer_md_tree(trees)

    return trees, p


def tree_refinement(trees):
    """A function that refines an ordered maximal slice tree partition, based on evaluating the
    active lists of nodes ("alpha-lists") of the nodes contained in the trees.

    Therefore, a bottom-up marking scheme is employed through which nodes that contradict the module property
    are identified. These nodes are labelled 'DEAD'. Consequently, after the trees have been refined,
    for each node u in Ti', every leaf x ∈ Lj, j > i, is either universal to or isolated from u if and only if
    neither u nor any of its descendants are labelled 'DEAD'. More importantly, all nodes, that are neither labelled
    'DEAD', nor have any of its descendants labelled 'DEAD', correspond to the modules not containing x
    after refinement.
    Additionally, new nodes are inserted into the tree, such that the nodes which are labelled 'DEAD' have exactly
    two children, which have the node's old children as their children.
    In regards to achieving a factorizing permutation at later stages of the algorithm, the order of their children
    is rearranged, depending on the index of the tree in which they reside.

    Note:
        The function does not return anything. Instead the objects corresponding to the trees are directly modified.

    Args:
        trees: A 'list' of 'Tree' objects, representing a  maximal slice tree partition T = T0, ..., Tk of some graph G,
            such that if L0, ..., Lk are the corresponding leaf sets, then Ti is the MD tree for G[Li].
            Moreover, each leaf x ∈ Li has an associated set α(x) consisting of its neighbours amongst
            the leaves of the Tj’s, j < i. (Neighbors amongst other maximal slice partitions are also contained in the
            set α(x), but their evaluation is of no interest here.)
    """

    # Identify all leaves in T
    all_leaves = set(leaf.node for tree in trees for leaf in tree.leaves())

    # Label each node u ∈ Ti, Ti ∈ T by the index of their Ti
    for i, tree in enumerate(trees):
        for u in tree:
            u.tree_index = i

    for tree in trees:
        for y in tree.leaves():

            # Compute the active alpha list α'(y) (active edges only involving nodes in T)
            # and update the alpha list α(y)
            y.node.active_alpha = y.node.alpha & all_leaves
            y.node.alpha = y.node.alpha - y.node.active_alpha

            # Sets to keep track of marked leaves, marked inner nodes and unmarked nodes with a marked child
            marked_leaves = set()
            marked_nodes = set()
            unmarked_nodes_with_a_marked_child = set()  # Nodes to refine

            # Traverse the active alpha list α'(y) and mark each leaf
            for node in y.node.active_alpha:
                node.container.is_marked = True
                marked_leaves.add(node.container)

                # Increase the mark count of the parent of the marked leaf
                if node.container.parent is not None:
                    node.container.parent.mark_count += 1
                    unmarked_nodes_with_a_marked_child.add(node.container.parent)

            # For each marked leaf: Mark their ancestors, if they are parent to only marked children
            for t_node in marked_leaves:
                parent = t_node.parent
                while parent is not None:
                    if parent.mark_count == len(parent.children):
                        if parent.parent is not None and not parent.is_marked:
                            parent.parent.mark_count += 1
                            if not parent.parent.is_marked:
                                unmarked_nodes_with_a_marked_child.add(parent.parent)

                        parent.is_marked = True
                        marked_nodes.add(parent)
                        unmarked_nodes_with_a_marked_child.discard(parent)

                        parent = parent.parent

                    else:
                        if any(c.is_marked for c in parent.children):
                            unmarked_nodes_with_a_marked_child.add(parent)
                        break

            for u in unmarked_nodes_with_a_marked_child:
                # Let A be the set of marked children of u, and let B be its other children
                a, b = u.group_children(lambda x: x.is_marked)

                # If |A| > 1 and u is degenerate
                if len(a) > 1 and u.is_degenerate():
                    # Replace the children in A with a new marked node inheriting u’s type,
                    # whose children are those nodes in A
                    u.replace_children(a).is_marked = True

                # If |B| > 1 and u is degenerate
                if len(b) > 1 and u.is_degenerate():
                    # Replace the children in B with a new unmarked node inheriting u’s type,
                    # whose children are those nodes in B
                    u.replace_children(b).is_marked = False

                # Label u as 'DEAD', if u is not labelled 'DEAD'
                if u.label is not Label.DEAD:
                    u.label = Label.DEAD

                    # Group u's children in marked and unmarked children
                    marked, unmarked = u.group_children(lambda x: x.is_marked)

                    if u.tree_index == 1:
                        # Make u’s marked child its left child and u’s unmarked child its right child
                        u.children = [*marked, *unmarked]

                    else:
                        # Make u’s marked child its right child and make u’s unmarked child its left child
                        u.children = [*unmarked, *marked]

            # Finally clear the marks of the nodes and set back their mark counters
            for t_node in marked_leaves | marked_nodes | unmarked_nodes_with_a_marked_child:
                t_node.is_marked = False
                t_node.mark_count = 0


def factorize(trees):
    """A function, that modifies a maximal slice tree partition T = T0, ..., Tk of some graph G, as produced by
    'tree_refinement()', where T0 = x is the pivot, and L0, ..., Lk are the corresponding leaf sets,
    in such a way, that - except for the position of the pivot - a factorizing permutation is obtained.

    After the trees in the maximal slice tree partition have been refined by 'tree_refinement', some of the nodes that
    contradict the module property are identified and labelled 'DEAD'. As a consequence, their ancestors cannot
    correspond to modules either. Therefore, these nodes are labelled 'ZOMBIE'.
    The trees are now modified in such a way, that for all nodes that carry the 'ZOMBIE' label, the order of their
    children is rearranged. If a 'ZOMBIE'-labelled nodes is degenerate and has multiple unlabelled children, these are
    grouped under a new new node of the same type. This new node becomes a child of the 'ZOMBIE'-labelled node.
    This leads to the fact, that if M is a strong module, then M − {x} appears consecutively in σ(T').
    Moreover, the vertices in each co-component of G[L1], and each component of G[Li], i > 1, also appear consecutively.

    Lastly, all nodes that have a parent which is either labelled 'DEAD' or 'ZOMBIE', have their parent set to 'None'.
    This modification allows for easy identification of the (co-)components in 'pivot_factorizing_permutation()',
    while at the same time, whenever 'get_root()' is called on a leaf node, the returned tree will be in full harmony
    with the module property, as it will be free of nodes that are labelled 'DEAD' or 'ZOMBIE'.

    Note:
        The function does not return anything. Instead the objects corresponding to the trees are directly modified.

    Args:
        trees: A 'list' of 'Tree' objects, representing a maximal slice tree partition T = T0, ..., Tk of some graph G,
            as produced by 'tree_refinement()', where T0 = x is the pivot, and L0, ..., Lk are the corresponding leaf
            sets.
    """

    # For each Ti ∈ T
    for i, tree_i in enumerate(trees):

        # For each node u ∈ Ti labelled 'DEAD'
        for u in tree_i.nodes_by_label(Label.DEAD):

            # Label all of u's ancestors as 'ZOMBIE' unless they are labelled 'DEAD'
            for t_node in u.ancestors():
                if t_node.label is Label.ZOMBIE:  # All ancestors are already labelled 'ZOMBIE' (or remain 'DEAD')
                    break
                if t_node.label is not Label.DEAD:
                    t_node.label = Label.ZOMBIE

        # For each node u ∈ Ti labelled 'ZOMBIE'
        for u in tree_i.nodes_by_label(Label.ZOMBIE):

            # Let A be the children of u that are labelled 'DEAD' or 'ZOMBIE', and let B be its other children
            a, b = u.group_children(lambda x: x.label is Label.DEAD or x.label is Label.ZOMBIE)

            if len(b) > 1 and u.is_degenerate():
                # Replace the children in B with a new marked node inheriting u's type,
                # whose children are those nodes in B
                u.replace_children(b)

            # Let A be the children of u that are labelled 'DEAD' or 'ZOMBIE', and let B be its other children
            a, b = u.group_children(lambda x: x.label is Label.DEAD or x.label is Label.ZOMBIE)

            # If i = 1 then order the children of u so that those in A appear first
            if i == 1:
                u.children = [*a, *b]

            # Else order the children of u so that those in A appear last
            else:
                u.children = [*b, *a]

        # Clear all labels and set the parent of the children of 'DEAD' or 'ZOMBIE' nodes to 'None'
        for t_node in tree_i:
            if t_node.label is Label.DEAD or t_node.label is Label.ZOMBIE:
                t_node.label = None
                for child in t_node.children:
                    child.parent = None


def build_spine(sigma):
    """A function that a computes a rooted tree T, whose nodes correspond to the strong modules containing x.

    The function utilizes a pivot factorizing permutation σ = Ca′,...,C1′,x,C1,...,Cb for which μ(Ci′) has been
    computed for each Ci', and for which μ(Ci) and ρ(Ci) have been computed for each Ci, to compute a rooted tree T,
    whose nodes correspond to the strong modules containing x.
    In doing so, the function is taking into account the property of the μ- and ρ-values to determine the boundaries of
    these strong modules, while taking advantage of the fact that the strong modules containing x appear consecutively
    in σ.
    Technically a loop is employed, where one strong module M containing x is recognized per iteration. Firstly, the
    attempt to detect a 'SERIES' module is made, secondly the function will try to recognize a 'PARALLEL' module and
    finally a 'PRIME'module.
    Once a module is detected, in the form that the (co-)components belonging to this module have been identified,
    a new node is created which has these (co-)components and the tree created in previous iterations as its children.
    This way, a rooted tree T is iteratively computed, in which the nodes - except for the leaves - correspond to the
    strong modules containing x. (Note that the tree T at the beginning only contains to the leaf x.)

    To detect a 'SERIES' module, the co-components are considered. Therefore, the left index l is first off incremented,
    then μ(C'l) is evaluated. This may yield that the module does not contain any components in which case the
    co-component is added to the module. More co-components are tried out, until one co-component that does not belong
    to this 'SERIES' module is encountered.
    Then, if no 'SERIES' module was found, the function will try to detect a 'PARALLEL' module in an analogous manner.
    Only if this also fails, a 'PRIME' module is tried out. Here, the left and the right index are simultaneously
    incremented. From the μ- and ρ-values of the (co-)components C'l and Cr follow the limits of the module according
    to these initially considered (co-)components. The μ- and ρ-values for the (co-)components within this range,
    now have to be evaluated, which may yield new limits.
    This process is repeated until the module's limits is determined.

    Args:
        sigma: A 'PivotFactorizingPermutation', representing  pivot factorizing permutation
            σ = Ca′,...,C1′,x,C1,...,Cb for which μ(Ci′) has been computed for each Ci', and for which μ(Ci) and
            ρ(Ci) have been computed for each Ci. (See 'pivot_factorizing_permutation()' for details.)

    Returns:
        A rooted tree T whose nodes correspond to the strong modules containing x, each one properly labelled by
        the module's type, where the leaves of T are the elements of σ, and each node and leaf is descendent
        from all strong modules containing it.

    """

    # T ← x
    tree = sigma.pivot

    # Determine the number of (co-)component
    a, b = len(sigma.co_components), len(sigma.components)

    # Initialise the left / right indices.
    l, r = 0, 0

    # while l != a or r!= b do
    while l != a or r != b:

        # No (co-)components have been added to the module yet
        contains_co_component, contains_component = False, False

        # M ← ∅; The strong module containing x that will be identified this iteration
        module = []

        # # Locating 'SERIES' modules # #

        # Increment the left index to check the first co-component in this iteration
        l += 1

        # While l ≤ a and μ(C'l) = r
        while l <= a and sigma.co_components[l - 1].mu == r:
            # M ← M ∪ {C'l}
            module.append(sigma.co_components[l - 1].co_component)
            contains_co_component = True

            # Increment the left index to check the next co-component
            l += 1

        # Decrement the left index, as the last checked co-component was not "legal"
        l -= 1

        # # Locating 'PARALLEL' modules # #

        # If M = ∅
        if len(module) == 0:

            # Increment the right index to check the first component in this iteration
            r += 1

            # While r ≤ b and μ(Cr) = l and ρ(Cr) = 0
            while r <= b and sigma.components[r - 1].mu == l and sigma.components[r - 1].rho == 0:
                # M ← M ∪ {Cr}
                module.append(sigma.components[r - 1].component)
                contains_component = True

                # Increment the left index to check the next co-component
                r += 1

            # Decrement the right index, as the last checked component was not "legal"
            r -= 1

        # # Locating PRIME modules # #

        # If M = ∅
        if len(module) == 0:

            # Increment the left and right index to check the first co-component and the first component in this
            # iteration
            l += 1
            r += 1

            # Initialise l', r'
            # l' ← l; r' ← r
            l_, r_ = l, r

            # t ← max{μ(Cr), l}
            t = max(sigma.components[r - 1].mu, l)

            # m ← max{μ(C'l), ρ(Cr), r}
            m = max(sigma.co_components[l - 1].mu, sigma.components[r - 1].rho, r)

            # while t != l_ and m != r_:
            while True:
                # Save the old values
                # t' ← t; m' ← m
                t_, m_ = t, m

                # t ← max{max{μ(Ci) | i ∈ [r', m]}, t}
                t = max(max(sigma.components[i - 1].mu for i in range(r_, m + 1)), t)

                # m ← max{max{μ(C'i) | i ∈ [l', t]}, max{ρ(Ci | i ∈ [r', m]}, m}
                m = max(max(sigma.co_components[i - 1].mu for i in range(l_, t + 1)),
                        max(sigma.components[i - 1].rho for i in range(r_, m + 1)), m)

                # Update l', r'
                # l' ← t'; r' ← m'
                l_, r_ = t_, m_

                # Break the loop, if the module's maximal limits have been found
                if t_ == t and m_ == m:
                    break

            # M ← M ∪ {C'i | i ∈ [l, t]}
            for i in range(l, t + 1):
                module.append(sigma.co_components[i - 1].co_component)
                contains_co_component = True

            # M ← M ∪ {Ci | i ∈ [r, m]}
            for i in range(r, m + 1):
                module.append(sigma.components[i - 1].component)
                contains_component = True

            # Update l, r
            # l ← t; r ← m
            l, r = t, m

        # Create a new node u with the elements of M as its children
        u = Tree(Type.NODE)  # The type is unimportant here
        for element in module:
            u.insert(Tree(Type.NODE, element))

        # Label u as 'SERIES' if there is no Ci ∈ M
        if not contains_component:
            u.type = Type.SERIES

        # Label u as 'PARALLEL' if there is no C'i ∈ M
        elif not contains_co_component:
            u.type = Type.PARALLEL

        # Otherwise, label u as 'PRIME'
        else:
            u.type = Type.PRIME

        # Update T by making u the parent of T's root
        u.insert(tree)
        tree = u

    # return T
    return tree


def pivot_factorizing_permutation(trees):
    """A rather technical function, which prepares a maximal slice tree partition T = T0, ..., Tk of some graph G,
    as produced by 'factorize()', where T0 = x is the pivot, for further processing by 'build_spine()'.

    After the maximal slice tree partition T has been modified by 'factorise()', it virtually represents a factorizing
    permutation, in the way that if M is a strong module, then M − {x} appears consecutively in σ(T).
    Moreover, the vertices in each co-component of G[L1], and each component of G[Li], i > 1, also appear consecutively.
    It remains to identify the (co-)component within σ(T) and thus the position of the pivot x, and to group the
    (co-)components accordingly for further processing.
    In order to be able to delineate the boundaries of a module M containing the pivot x (in 'build_spine()'),
    μ- and ρ-values for each (co-)component are required. These are computed here and bundled together with
    the (co-)components.

    Args:
        trees: A 'list' of 'Tree' objects, representing a maximal slice tree partition T = T0, ..., Tk of some graph G,
            as produced by 'factorize()', where T0 = x is the pivot, and L0, ..., Lk are the corresponding leaf sets.
            Additionally, each leaf x ∈ Li has been labelled according to either its component in G[Li] for i > 1 or to
            its co-component in G[Li] for i = 1.

    Returns:
        A 'PivotFactorizingPermutation'('namedtuple') having the attributes 'pivot', 'co_components' and 'components'.
        'pivot' is a 'Tree' object representing the pivot x = T0.
        'co_components' is a 'list' of 'CoComponent' objects ('namedtuple') with the attributes 'co_component' and
        'mu' where 'co_component' is a 'frozenset' of 'Tree' objects representing the nodes in the co_component and 'mu'
        is the maximal μ-value of the nodes in the component.
        'components' is analog to 'co_components', except for an additional 'rho' attribute representing the maximal
        ρ-value amongst the nodes in the component.
    """

    # Two lists for the (co-)components
    co_components = []
    components = []

    # For Ti ∈ T, i ∈ [1, k]
    for i, tree in enumerate(trees[1:], 1):
        # If i = 1 then insert all l ∈ Li into 'co_components'
        if i == 1:
            for t_node in tree.leaves():
                co_components.append(t_node)
        # Else insert all l ∈ Li into 'components'
        else:
            for t_node in tree.leaves():
                components.append(t_node)

    # Group the nodes in 'co_components' / 'components' by their 'connectivity' label
    co_components = [frozenset(cc) for key, cc in groupby(co_components, key=lambda x: x.connectivity)]
    co_components.reverse()  # Reverse 'co_components' as it is descendingly indexed
    components = [frozenset(c) for key, c in groupby(components, key=lambda x: x.connectivity)]

    def is_adjacent_to_component(quantifier_fn, node, component):
        """A function that checks whether a node is adjacent to (any/all) nodes in a component.

        Args:
            quantifier_fn: A quantifier function. Depending on the case, 'any()' or 'all()' is handed in
                as a function here.
            node: The node for which to check its adjacency to the nodes in the component.
            component: The component for which to check its adjacency to the node.

        Returns:
            'True' if a node is adjacent to (any/all) nodes in the component, 'False' else.
        """

        def is_adjacent(u, v):
            """A function that checks whether two nodes are adjacent to each other.

            Args:
                u: The first node.
                v: The second node.
            Returns:
                'True' if 'u' is adjacent to 'v' (and vice versa), 'False' else.
            """

            return u.node in v.node.adjacent

        return quantifier_fn(is_adjacent(node, n) for n in component)

    # Compute μ(l) for each l ∈ Li, i ∈ [1, k]
    a, b = len(co_components), len(components)
    for i, tree in enumerate(trees[1:], 1):
        if i == 1:
            # For each y ∈ L1, let μ(y) be the smallest j (possibly j = 0)
            # such that every z ∈ Cl, l > j, is non-adjacent to y.
            for y in tree.leaves():
                j = b
                while j > 0 and not is_adjacent_to_component(any, y, components[j - 1]):
                    j -= 1
                y.mu = j
        else:
            # For each w ∈ Li, i > 1, let μ(y) be the smallest j (possibly j = 0)
            # such that every z ∈ C'l, l > j, is adjacent to y.
            for y in tree.leaves():
                j = a
                while j > 0 and is_adjacent_to_component(all, y, co_components[j - 1]):
                    j -= 1
                y.mu = j

    # Compute ρ(l) for each l ∈ Li, i ∈ [2, k]
    # For each y ∈ Ci, 1 ≤ i ≤ b, let ρ(y) be the largest j > i such that
    # there exists a z ∈ Cj to whom y is adjacent; if no such j exists, then ρ(y) = 0.
    for i in range(1, b + 1):
        for y in components[i - 1]:
            y.rho = 0
            for j in range(b, i, -1):
                if is_adjacent_to_component(any, y, components[j - 1]):
                    y.rho = j
                    break

    # Declare the 'CoComponent' / 'Component' type
    CoComponent = namedtuple('CoComponent', 'co_component, mu')
    Component = namedtuple('Component', 'component, mu, rho')

    # Calculate μ(C'i), μ(Ci), ρ(Ci) for each (co-)component
    # μ(C') := max{μ(y) | y ∈ C'}; μ(C) := max{μ(y) | y ∈ C}; ρ(C) := max{ρ(y) | y ∈ C}
    co_components = [CoComponent(cc, max(node.mu for node in cc)) for cc in co_components]
    components = [Component(c, max(node.mu for node in c), max(node.rho for node in c)) for c in components]

    # Declare the 'PivotFactorizationPermutation' type
    PivotFactorizingPermutation = namedtuple('PivotFactorizingPermutation', 'pivot, co_components, components')

    return PivotFactorizingPermutation(trees[0], co_components, components)


def conquer_md_tree(trees):
    """A function, that builds the modular decomposition tree for a graph G from a maximal slice tree
    partition T = T0, ..., Tk of this graph.

    This function begins with determining, whether the graph G is disconnected or not. For this purpose, the set α(x)
    is examined for some leaf x ∈ Tk. If the graph G is disconnected, the function will at first only process the
    maximal slice tree partition T = T0, ...,Tk-1 and thus compute the modular decomposition tree for G[V(G)-Lk].
    Only in the end, it combines it with the modular decomposition tree for G[Lk] to form the modular decomposition tree
    for the graph G.
    If the graph G is connected, then the complete maximal slice tree partition is processed throughout the function,
    thereby computing the modular decomposition tree for G "directly".
    As a next step, each leaf x ∈ Li is labelled according to either its component in G[Li] for i > 1 or to its
    co-component in G[Li] for i = 1.
    Through calls to 'tree_refinement()', 'factorize()' and 'pivot_factorizing_permutation()' a pivot factorizing
    permutation σ = Ca', ..., C1', x, C1, ...,Cb is obtained, such that for each strong module M containing x
    there is a sequence Cc', ..., C1', x, C1, ..., Cd representing that module. This allows for building a rooted
    tree whose nodes correspond to the strong modules containing x ('build_spine()').
    However, the leaves of this tree only correspond to (co-)components, hence the function proceeds with replacing
    these (co-)components with their corresponding trees Ti ∈ T (maximal slice tree partition after 'factorize').
    As previously mentioned, depending on whether the root of the modular decomposition tree will be 'PARALLEL' or not,
    the tree for T = T0, ...,Tk-1 will be combined with the tree Tk.
    Finally, a scan through the tree detects degenerate nodes, which have a parent of the same type. These nodes are
    then merged, before the modular decomposition tree for the graph G is returned.

    Args:
        trees: A maximal slice tree partition T = T0 , ..., Tk of a graph G, such that if L0, ..., Lk
            are the corresponding leaf sets, then Ti is the MD tree for G[Li]. Moreover, each leaf x ∈ Li has an
            associated set α(x) consisting of its neighbours amongst the leaves of the Tj’s, j < i. (Neighbors amongst
            other maximal slice partitions are also contained in the set α(x), but their evaluation is of no interest
            here.)

    Returns:
        The modular decomposition tree for G.
    """

    # Compute L = L0 ∪ L1 ∪ ... ∪ Lk-1
    all_leaves_except_last_tree = set(leaf.node for tree in trees[:-1] for leaf in tree.leaves())

    # If there is no y ∈ Lk such that |α(y) ∩ L| > 0 then k'← k−1; else k'← k
    # If y,z ∈ L(k), then alpha(y) = alpha(z), therefore it suffices to only examine α(y) for one sample y ∈ Lk
    k = len(trees) - 1
    k_ = k - 1
    y = next(trees[-1].leaves())
    if len(y.node.alpha & all_leaves_except_last_tree) > 0:
        k_ = k

    # T = T0, ..., Tk'
    trees_ = trees[:k_ + 1]

    # a: number of co-components, b: number of components
    a, b = 0, 0

    # Label the leaves of the trees Ti's. Ti ∈ T, i ∈ [1, k']
    for i, tree in enumerate(trees_[1:], 1):

        # If i = 1 then label the leaves in Li by their co-components in G[Li]
        if i == 1:
            a = tree.label_by_component(Connectivity.CO_COMPONENT)

        # Else label the leaves in Li by their components in G[Li]
        else:
            b = tree.label_by_component(Connectivity.COMPONENT, b)

    # Refine the tree partition T = T0, ..., Tk'
    tree_refinement(trees_)  # TODO

    # Factorize the tree partition T = T0, ..., Tk'
    factorize(trees_)

    # Compute the pivot factorizing permutation σ = C'a, ..., C'1, x, C1, ...,Cb defined by T
    sigma = pivot_factorizing_permutation(trees_)

    # Build a rooted tree whose nodes correspond to the strong modules containing x
    tree = build_spine(sigma)

    # Replace the leaves (co-components) of the tree with the corresponding trees in T
    replaced = set()
    for leaf in tree.leaves():
        if type(leaf.node) != Node:  # A (co-)component
            not_replaced = set(i for i in leaf.node)  # Nodes in the (co-)component that are not yet in the tree
            for t_node in leaf.node:  # Iterating through the component as the frozenset
                if t_node in replaced:  # Node has been replaced
                    continue
                if t_node in not_replaced:  # This node is not already in the tree, in the form "the corresponding tree"
                    root = t_node.get_root()  # Get the root of the tree, that this vertex is a leaf of
                    leaf.parent.insert(root)  # Insert the tree
                    not_replaced = not_replaced.difference(root.leaves())  # Update 'not_replaced'
                    for node in root.leaves():  # Update 'replaced'
                        replaced.add(node)

    # Remove the (co-)components
    for leaf in list(tree.leaves()):
        if type(leaf.node) != Node:
            leaf.parent.children.remove(leaf)

    # Update the tree, depending on whether G is disconnected (k' = k - 1)
    if k_ == k - 1:
        # If Tk''s root is parallel
        if trees[k].type == Type.PARALLEL:
            # Update the tree by making the root of Tk' the parent of the tree's root
            trees[k].insert(tree)
            tree = trees[k]
        else:
            # Update the tree by adding a new parallel node as the parent of the trees's root
            # and add the root of Tk' as a child of this new root
            new_node = Tree(Type.PARALLEL)
            new_node.insert(tree)
            new_node.insert(trees[k])
            tree = new_node

    # For each degenerate node u in the tree whose parent has the same type, replace u by its children
    for t_node in tree:
        if t_node.parent is not None and t_node.type == t_node.parent.type and t_node.is_degenerate():
            for child in t_node.children:
                t_node.parent.insert(child)
            t_node.parent.children.remove(t_node)

    # Return the modular decomposition tree for G
    return tree
