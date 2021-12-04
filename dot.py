"""I/O functions.

This module implements the functions required for reading in a graph from a .dot-file, writing a tree to a .dot-file
and the rendering of the corresponding .dot-files.

Note: These functions only work with basic .dot-files - no styling, no labels , etc.
   Due to this implementation, using semicolons to end a line is mandatory!
   See './small_graphs_dot' for examples and 'https://graphviz.org/' for further information.
"""

from graphviz import Source, Graph as DGraph
from md import *


def path_to_dot(dot_path):
    """A function that reads the string from a .dot-file and returns it.

    Args:
        dot_path: The path to a .dot-file.

    Returns:
        The string contained in the .dot-file.
    """

    dot_file = open(dot_path)
    dot_str = dot_file.read()
    dot_file.close()
    return dot_str


def render_graph(dot_path, graph_name, engine_="dot", show=True):
    """A function that renders a graph (provided by a path) and saves its corresponding .dot-file and its corresponding
    .pdf-file in './graphs/' under the names ''graph_name'.dot' and ''graph_name'.dot.pdf'.

    Args:
        dot_path: The path to the graph.
        graph_name: The name of the graph used for naming the .dot-file.
        engine_: The rendering program used for rendering the graph.
    """

    source = Source.from_file(dot_path, engine=engine_)  # engines: dot, neato, fdp, sfdp, twopi, circo
    pdf_path = "./graphs/" + graph_name + ".dot"
    if show:
        source.render(pdf_path, view=True)  # Also creates .dot-file
    else:
        source.save(pdf_path)


def render_from_source(source_str, engine_="dot", show=True):
    """A function that renders a graph (provided by a string in the .dot-language) and saves its corresponding .dot-file and its corresponding
    .pdf-file in './graphs/' under the names 'your_graph.dot' and 'your_graph.dot.pdf'. and saves it as
    a .pdf-file in './graphs/' under the name 'your_graph.dot'.

    Args:
        source_str: The string describing the graph.
        engine_: The rendering program used for rendering the graph.
    """

    source = Source(source_str, engine=engine_)
    render_to_path = "./graphs/your_graph.dot"
    if show:
        source.render(render_to_path, view=True)  # Also creates .dot-file
    else:
        source.save(render_to_path)


def dot_to_graph(dot_str):
    """A function that creates a new 'Graph' object from a string in the .dot-language representing that graph.

    Args:
        dot_str: The raw string contained in a .dot-file.

    Returns:
        A 'Graph' object representing the graph.
    """

    # Get rid of all the duplicate whitespaces and newline characters
    without_whitespace = "".join(dot_str.split())

    # Find indices of opening and closing bracket
    open_bracket_idx = without_whitespace.find("{")
    close_bracket_idx = without_whitespace.find("}")

    if open_bracket_idx == -1 or close_bracket_idx == -1:
        raise Exception("no brackets found")

    # Get the string describing the graph (nodes / edges) and divide it by the semicolons
    content = without_whitespace[open_bracket_idx + 1:close_bracket_idx - 1]
    lines = content.split(";")

    # Build the graph
    graph = Graph()
    for l in lines:
        nodes = l.split("--")
        for v in nodes:
            graph.add_node(Node(v))
        for i in range(0, len(nodes) - 1):
            graph.add_edge(nodes[i], nodes[i + 1])

    return graph


def tree_to_dot(tree, tree_name, show=True):
    """A function that creates and renders a .dot-file describing a modular decomposition tree.
    The associated .dot-file and .pdf-file are saved in './md_trees/' under the names
    ''tree_name'.dot' and ''tree_name'.dot.pdf'.

    Args:
        tree: The 'Tree' object describing a modular decomposition tree.
        tree_name: The name of the tree (corresponding to a graph) used for naming the .dot-file.
        show: A boolean. If true the tree is rendered as a .pdf-file.

    """

    all_nodes = list(tree)  # A list of all the nodes contained in the tree
    dot = DGraph()  # A directed graph (.dot)

    for p in tree:
        # Label the nodes in the .dot-file by either their type (modules) or their id (leaves)
        parent_label = p.type.name if not (p.type is Type.NODE) else p.node.id

        # Create a node.
        # Use the index of the node in 'all_nodes' as a key to differentiate between nodes (modules) of the same type
        dot.node(str(all_nodes.index(p)), parent_label)

        for c in p.children:
            child_label = c.type.name if not (c.type is Type.NODE) else c.node.id
            dot.node(str(all_nodes.index(c)), child_label)  # Create a node
            dot.edge(str(all_nodes.index(p)), str(all_nodes.index(c)))  # Create an edge

    tree_path = "./md_trees/" + tree_name + ".dot"
    if show:
        dot.render(tree_path, view=True)  # Also creates .dot-file
    else:
        dot.save(tree_path)


def write_graph_to_dot(graph, graph_name, show=True, engine_="dot"):  # and render
    """A function that creates and renders a .dot-file describing a graph.
        The associated .dot-file and .pdf-file are saved in './graphs/' under the names
        ''graph_name'.dot' and ''graph_name'.dot.pdf'.

        Args:
            graph: The 'Graph' object describing a graph.
            graph_name: The name of the graph used for naming the .dot-file.
            show: A boolean. If true the graph is rendered as a .pdf-file.
            engine_: The rendering-engine used to render the .pdf-file.
    """

    dot_str = "graph\n{\n"
    nodes = list(graph.get_nodes())
    number_nodes, number_edges = 0, 0
    for node in nodes:
        number_nodes += 1
        dot_str += node.id + ";\n"
        for neighbor in node.adjacent:
            if neighbor.id > node.id:
                number_edges += 1
                dot_str += node.id + "--" + neighbor.id + ";\n"
    dot_str += "}"
    graph_file_name = "./graphs/" + graph_name + ".dot"
    graph_dot_file = open(graph_file_name, 'w')
    graph_dot_file.write(dot_str)
    graph_dot_file.close()

    graph_name = graph_name
    source = Source(dot_str, engine=engine_)  # engines: dot, neato, fdp, sfdp, twopi, circo, (osage, patchwork)
    render_to_path = "./graphs/" + graph_name + ".dot"
    if show:
        source.render(render_to_path, view=True)  # Also creates .dot-file
    else:
        source.save(render_to_path)

    return number_nodes, number_edges
