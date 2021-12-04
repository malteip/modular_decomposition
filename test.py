"""Test functions.

This module implements various functions for testing the implementation.
"""

from graph_generators import *
from md import *
from time import time
import sys
import scipy.special
import cProfile
import random


def prim_test():
    for n in [10, 100, 1000]:
        for p in range(0, 101, 1):
            prim_count = 0
            for i in range(1000):
                graph, _ = random_graph(n, p / 100)
                tree = md_tree(graph)
                if tree.type == Type.PRIME and len(tree.children) == n:
                    prim_count += 1
            print(n, p, prim_count/1000)
            sys.stdout.flush()


def test_m():  # fixed number of nodes; vary the edge probability
    for graph_order in range(1000, 6000, 1000):
        for edge_probability in range(5, 100, 5):
            total_time = 0
            for i in range(5):
                graph, _ = random_graph(graph_order, edge_probability/100)
                begin = time()
                md_tree(graph)
                end = time()
                total_time += end - begin
            print(graph_order, edge_probability, total_time / 5)
            sys.stdout.flush()


def test_n():  # fixed number of edges; vary the number of nodes
    for m in range(50000, 550000, 100000):
        for n in range(1000, 5200, 200):
            total_time = 0
            p = m / scipy.special.comb(n, 2)
            for i in range(5):
                graph, _ = random_graph(n, p)
                begin = time()
                md_tree(graph)
                end = time()
                total_time += end - begin
            print(n, m, total_time / 5)
            sys.stdout.flush()


def test_mw():  # modular width test; vary mw/md for graph with n = 1000, m ≈ 249750
    m_opt = 249750  # m(G(n=1000, p=0.5))
    e = 0.05  # error
    runs = 10

    for md in [Mode.RANDOM, Mode.DEEP, Mode.WIDE]:
        for mw in range(0, 1010, 10):
            total_time = 0
            for i in range(runs):
                while 1:
                    p = random.uniform(0.25, 0.75)
                    if mw > 0:
                        graph, _ = mw_bound_graph2(graph_order=1000, lo_mw_bound=mw, hi_mw_bound=mw,
                                                   edge_probability=p, mode=md)
                    else:  # cograph
                        graph, _ = mw_bound_graph2(graph_order=1000, lo_mw_bound=2, hi_mw_bound=2,
                                                   edge_probability=p, mode=md)

                    m = 0  # count edges
                    for node in graph.get_nodes():
                        for neighbor in node.adjacent:
                            if neighbor.id > node.id:
                                m += 1

                    if (m_opt - m_opt * e) <= m <= (m_opt + m_opt * e):  # e = 0.05: 474525 <= m <= 524475
                        begin = time()
                        md_tree(graph)
                        end = time()
                        total_time += end - begin
                        break

            if md == Mode.RANDOM:
                mode = 'r'
            if md == Mode.DEEP:
                mode = 'd'
            if md == Mode.WIDE:
                mode = 'w'

            print(mode, mw, total_time / runs)
            sys.stdout.flush()


def test_mode(mode):
    switcher = {
        'p': prim_test,
        'm': test_m,
        'n': test_n,
        'mw': test_mw,
    }

    test = switcher.get(mode, lambda: "Invalid arguments")
    test()


if __name__ == "__main__":
    test_mode(sys.argv[1])
