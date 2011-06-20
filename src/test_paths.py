#!/usr/bin/env python
'''Validate shortest-paths algorithms.'''

import logging
import unittest

import networkx as nx

from lib.graph import set_unit_weights, nx_graph_from_tuples, pathlen
from topo.os3e import OS3EGraph
from os3e_weighted import OS3EWeightedGraph
from paths import BFS, two_step_edge_disjoint_pair
from paths import two_step_vertex_disjoint_pair, edge_disjoint_shortest_pair


lg = logging.getLogger("test_paths")


# Figure 2.1, pg 23
graph_fig_2_1 = nx_graph_from_tuples([
    ('A', 'B', 1),
    ('A', 'C', 3),
    ('A', 'D', 5),
    ('B', 'C', 1),
    ('B', 'Z', 3),
    ('C', 'D', 2),
    ('C', 'Z', 1),
    ('D', 'E', 2),
    ('D', 'Z', 4),
    ('E', 'Z', 2)
])


# Figure 2.3, pg 27
graph_fig_2_3 = nx_graph_from_tuples([
    ('A', 'B', 5),
    ('A', 'D', 7),
    ('B', 'C', 1),
    ('B', 'Z', 8),
    ('D', 'E', 2),
    ('D', 'Z', 6)
],
[
    ('C', 'A', -1),
    ('E', 'C', -6),
    ('Z', 'E', -2)
])

# Figure 3.1a, pg 41
graph_fig_3_1_a = nx_graph_from_tuples([
    ('A', 'B', 1),
    ('A', 'E', 1),
    ('A', 'G', 8),
    ('B', 'C', 1),
    ('B', 'E', 1),
    ('B', 'F', 2),
    ('C', 'D', 1),
    ('C', 'G', 1),
    ('D', 'F', 1),
    ('D', 'Z', 1),
    ('E', 'F', 4),
    ('F', 'Z', 4),
    ('G', 'Z', 2)
])

# Figure 3.13a, pg 65
graph_fig_3_13_a = nx_graph_from_tuples([
    ('A', 'B', 1),
    ('A', 'G', 1),
    ('A', 'I', 7),
    ('B', 'C', 1),
    ('B', 'I', 2),
    ('C', 'D', 1),
    ('C', 'G', 2),
    ('D', 'E', 1),
    ('D', 'G', 5),
    ('D', 'H', 2),
    ('E', 'F', 1),
    ('E', 'H', 2),
    ('E', 'I', 3),
    ('F', 'Z', 1),
    ('F', 'I', 3),
    ('G', 'H', 8),
    ('H', 'Z', 4),
    ('I', 'Z', 5)
])

def compare_path_lists(test, one, two):
    '''Compare two path lists.

    Useful because shortest path algorithms yield paths in arbitrary orders.
    '''
    def make_tuple_set(path_list):
        return set([tuple(path) for path in path_list])

    test.assertEqual(make_tuple_set(one), make_tuple_set(two))


class TestBFS(unittest.TestCase):

    def test_line(self):
        '''Check shortest path for line graph.'''
        # Return the line graph with n nodes, lowest-num node is 0
        for i in range(2, 4):
            g = nx.path_graph(i)
            set_unit_weights(g)
            path = BFS(g, 0, i - 1)
            self.assertTrue(path)
            self.assertEqual(path[0], 0)
            self.assertEqual(path[-1], i - 1)

    def test_disconnected(self):
        '''If no path exists, do we return None?'''
        g = nx.Graph()
        g.add_node('A')
        g.add_node('Z')
        path = BFS(g, 'A', 'Z')
        self.assertEquals(path, None)

    def test_example_2_5(self):
        '''Example 2.5 on pg. 34.'''
        path = BFS(graph_fig_2_1, 'A', 'Z')
        self.assertEqual(path, [i for i in 'ABCZ'])

    def test_example_2_6(self):
        '''Example 2.6 on pg. 35.'''
        g = graph_fig_2_3
        path = BFS(g, 'A', 'Z')
        self.assertEqual(path, [i for i in 'ADECBZ'])
        self.assertEqual(pathlen(g, path), 12)

    def test_example_3_1_a(self):
        '''Example 3.1a on pg. 41.'''
        g = graph_fig_3_1_a
        path = BFS(g, 'A', 'Z')
        self.assertEqual(path, [i for i in 'ABCDZ'])
        self.assertEqual(pathlen(g, path), 4)

    def test_example_3_13_a(self):
        '''Example 3.13a on pg 65.'''
        g = graph_fig_3_13_a
        path = BFS(g, 'A', 'Z')
        self.assertEqual(path, [i for i in 'ABCDEFZ'])
        self.assertEqual(pathlen(g, path), 6)


class TestTwoStepEdgeDisjointPair(unittest.TestCase):

    def test_example_3_1_b(self):
        '''Example 3.1b on pg 41.'''
        g = graph_fig_3_1_a
        paths = two_step_edge_disjoint_pair(g, 'A', 'Z')
        self.assertEqual(paths[0], [i for i in 'ABCDZ'])
        self.assertEqual(paths[1], [i for i in 'AEBFZ'])


class TestTwoStepVertexDisjointPair(unittest.TestCase):

    def test_example_3_1_c(self):
        '''Example 3.1c on pg 42.'''
        g = graph_fig_3_1_a
        paths = two_step_vertex_disjoint_pair(g, 'A', 'Z')
        self.assertEqual(paths[0], [i for i in 'ABCDZ'])
        self.assertEqual(paths[1], [i for i in 'AEFZ'])


class TestEdgeDisjointShortestPair(unittest.TestCase):

    def test_diamond(self):
        '''Simple diamond graph w/two equal paths.'''
        g = nx.Graph()
        g.add_path(['A', 'B', 'Z', 'C', 'A'])
        set_unit_weights(g)
        paths = edge_disjoint_shortest_pair(g, 'A', 'Z')
        exp_paths = [['A', 'B', 'Z'], ['A', 'C', 'Z']]
        compare_path_lists(self, paths, exp_paths)

    def test_example_3_13_a(self):
        '''Example 3.13a on pg 65.'''
        g = graph_fig_3_13_a
        paths = edge_disjoint_shortest_pair(g, 'A', 'Z')
        exp_paths = [[i for i in 'AGCDEFZ'], [i for i in 'ABIZ']]
        compare_path_lists(self, paths, exp_paths)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    unittest.main()