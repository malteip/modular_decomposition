"""Various functions for generating graphs.

This module implements various functions for generating graphs.

Note: 'random_graph()' and 'mw_bound_graph2()' can be used through the text-user-interface.
"""

from random import random, choice, randint
from dot import *


class Mode(Enum):
    """Labels for the assembly mode"""
    WIDE = auto()
    DEEP = auto()
    RANDOM = auto()


def random_graph(graph_order, edge_probability=0.5):  # binomial random graph
    graph = Graph()

    for u in range(graph_order):
        graph.add_node(Node(str(u + 1)))

    for u in range(graph_order):
        for v in range(u + 1, graph_order):
            if random() < edge_probability:
                graph.add_edge(str(u + 1), str(v + 1))

    graph_name = str(graph_order) + "_" + str(edge_probability)
    return graph, graph_name


def mw_bound_graph2(graph_order, lo_mw_bound, hi_mw_bound, edge_probability=0.5, mode=Mode.RANDOM):
    module_sizes = []
    while sum(module_sizes) - len(module_sizes) + 1 < graph_order:
        module_sizes.append(randint(lo_mw_bound, hi_mw_bound))

    nodes_in_graph = sum(module_sizes) - len(module_sizes) + 1
    diff = nodes_in_graph - graph_order
    if diff > 0:
        while diff != 0:
            if module_sizes[-1] > diff:
                module_sizes[-1] = module_sizes[-1] - diff
                diff = 0
            else:
                last = module_sizes.pop()
                diff = diff - last

    module_sizes.reverse()  # to keep derivation from mw bounds in leaves
    graphs = [random_prime_graph(mw, edge_probability)[0] for mw in module_sizes]
    uniquify_node_ids(graphs)
    graph = assemble_graph(graphs, mode)
    flatten_node_ids(graph)  # TODO better to not flatten to identify modules?
    graph_name = str(graph_order) \
        + "_[" + str(lo_mw_bound) + "," + str(hi_mw_bound) + "]_" \
        + str(edge_probability) + "_" + str(mode)[5:]

    return graph, graph_name


def is_prime(graph):  # TODO: prime labelling problem? wtf!
    tree = md_tree(graph)
    return tree.type == Type.PRIME and len(tree.children) == len(graph.get_nodes())


def random_prime_graph(graph_order, edge_probability=0.5):  # might return a cograph, if graph order is < 4
    # print(graph_order, "...")
    if graph_order < 4:
        return random_cograph(graph_order, edge_probability, Mode.RANDOM)
    while True:
        graph, graph_name = random_graph(graph_order, edge_probability)
        # print("-miss-")

        if is_prime(graph):
            graph_name = graph_name + "_prime"
            return graph, graph_name


def uniquify_node_ids(graphs):
    # unique ids (node.id and(!!) keys in graph.nodes)
    for i, graph in enumerate(graphs):
        for node in graph.get_nodes():
            old_node_id = node.id
            node.id = str(i + 1) + "." + node.id  # new unique node.id (+ 1 --> start ids at "1")
            graph.nodes[node.id] = graph.nodes[old_node_id]  # new dict entry under new id
            del graph.nodes[old_node_id]  # delete old entry


def flatten_node_ids(graph):
    for i, node in enumerate(list(graph.get_nodes())):
        old_node_id = node.id
        node.id = str(i + 1)
        graph.nodes[node.id] = graph.nodes[old_node_id]  # new dict entry under new id
        del graph.nodes[old_node_id]  # delete old entry


def replace_node_in_the_graph_with_graph(the_graph, node, graph):
    # add edges from each new_node in graph_to_insert TO each of node's neighbors in the_graph
    for new_node in graph.get_nodes():
        the_graph.add_node(new_node)
        for neighbor in node.adjacent:
            the_graph.add_edge(new_node.id, neighbor.id)  # TODO doesnt add nodes if node doesnt have neighbors

    # add the edges between nodes in graph_to_insert TO the_graph
    for new_node in graph.get_nodes():
        the_graph.nodes.get(new_node.id).adjacent = the_graph.nodes.get(new_node.id).adjacent.union(
            new_node.adjacent)

    the_graph.remove_node(node.id)


def random_cograph(graph_order, edge_probability=0.5, mode=Mode.RANDOM):
    if graph_order == 1:
        return random_graph(1, 0)
    else:
        graphs = [random_graph(2, edge_probability)[0] for i in range(graph_order - 1)]
        uniquify_node_ids(graphs)
        cograph = assemble_graph(graphs, mode)
        graph_name = str(graph_order) + "_" + str(edge_probability) + "_co"

        flatten_node_ids(cograph)
        return cograph, graph_name


def assemble_graph(graphs, mode):
    the_graph = graphs.pop()
    i = 0
    while len(graphs) != 0:
        if mode == Mode.WIDE:
            # assemble the graph so, that its md tree is as wide as possible.
            for node in list(the_graph.get_nodes()):
                if len(graphs) == 0:
                    break
                replace_node_in_the_graph_with_graph(the_graph, node, graphs.pop())

        if mode == Mode.RANDOM:
            i += 1
            # assemble the graph in a random manner.
            # the resulting md tree is potentially deeper than in WIDE mode, but shallower than in DEEP mode.
            node = choice(tuple(the_graph.get_nodes()))
            replace_node_in_the_graph_with_graph(the_graph, node, graphs.pop())

        if mode == Mode.DEEP:
            # assemble the graph so, that its md tree is as deep as possible.
            if i == 0:
                temp = graphs[-1]
                node = choice(tuple(the_graph.get_nodes()))
                replace_node_in_the_graph_with_graph(the_graph, node, graphs.pop())
                i += 1
            else:
                node_id = choice(tuple(temp.get_nodes())).id
                temp = graphs[-1]
                replace_node_in_the_graph_with_graph(the_graph, the_graph.nodes[node_id], graphs.pop())

    return the_graph


def mw_fractal_graph(graph_order, modular_width, edge_probability=0.5, mode=Mode.WIDE):
    number_of_modules = int((graph_order - 1) / (modular_width - 1))  # number of inner nodes in the md tree
    rest_module_mw = graph_order - (number_of_modules * (modular_width - 1) + 1)  # a number of nodes < modular_width

    graphs = []
    if rest_module_mw > 3:
        graphs.append(random_prime_graph(rest_module_mw + 1, edge_probability)[0])  # TODO: edge_probability param??

    else:
        graphs.append(random_cograph(rest_module_mw + 1, edge_probability, 1)[0])
        pass

    for i in range(number_of_modules):
        graphs.append(random_prime_graph(modular_width, random())[0])

    uniquify_node_ids(graphs)
    the_graph = assemble_graph(graphs, mode)

    graph_name = str(graph_order) + "_" + str(modular_width) + "_mwf"
    flatten_node_ids(the_graph)
    return the_graph, graph_name


def mw_bound_graph(graph_order, modular_width_bound, edge_probability=0.5, mode=Mode.RANDOM):
    module_sizes = []
    while sum(module_sizes) - len(module_sizes) + 1 < graph_order:
        module_sizes.append(randint(1, modular_width_bound))

    nodes_in_graph = sum(module_sizes) - len(module_sizes) + 1
    diff = nodes_in_graph - graph_order
    if diff > 0:
        while diff != 0:
            if module_sizes[-1] > diff:
                module_sizes[-1] = module_sizes[-1] - diff
                diff = 0
            else:
                last = module_sizes.pop()
                diff = diff - last

    graphs = [random_prime_graph(mw, edge_probability)[0] for mw in module_sizes]
    uniquify_node_ids(graphs)
    graph = assemble_graph(graphs, mode)
    flatten_node_ids(graph)
    graph_name = str(graph_order) + "_" + str(modular_width_bound) + "_mwb"

    return graph, graph_name


def uniform_random_graph(graph_order, number_of_edges):
    graph = Graph()

    for u in range(graph_order):
        graph.add_node(Node(str(u + 1)))

    edges = set()
    while len(edges) < number_of_edges:
        u = randint(1, graph_order)
        v = randint(1, graph_order)
        if u == v:
            continue
        if v < u:
            temp = u
            u = v
            v = temp
        edges.add((str(u), str(v)))

    for e in edges:
        graph.add_edge(*e)

    graph_name = str(graph_order) + "_" + str(number_of_edges)
    return graph, graph_name
