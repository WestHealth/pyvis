import unittest
from ..network import Network
import os


class NodeTestCase(unittest.TestCase):

    def setUp(self):
        self.g = Network()

    def test_one_node_g(self):
        self.g.add_node(0, 0)
        self.assertEqual(0, self.g.nodes[0]["id"])
        self.assertEqual(0, self.g.nodes[0]["label"])
        self.assertTrue(0 in self.g.get_nodes())

    def test_one_conn(self):
        self.g.add_nodes([0, 1])
        self.assertTrue(1 in self.g.get_nodes())
        self.assertTrue(0 in self.g.get_nodes())
        self.g.add_edge(0, 1)
        self.assertTrue(self.g.get_edges()[
                        0]["from"] == 0 and self.g.get_edges()[0]["to"] == 1)

    def test_no_dup_edges(self):
        self.g.add_nodes([0, 1])
        self.g.add_edge(0, 1)
        self.assertTrue(len(self.g.get_edges()) == 1)
        self.g.add_edge(1, 0)
        self.assertTrue(len(self.g.get_edges()) == 1)

    def test_no_dup_nodes(self):
        self.g.add_node(100, 100)
        self.g.add_node(100, 100)
        self.assertTrue(len(self.g.nodes) == 1)
        self.g.add_node(100, "n101")
        self.assertTrue(len(self.g.nodes) == 1)

    def test_node_labels(self):
        self.g.add_node(1, "n2")
        self.g.add_node(2, "n3")
        self.g.add_node(3, "n4")
        self.assertEqual(set(map(lambda s: s["label"], self.g.nodes)),
                         set(["n2", "n3", "n4"]))

    def test_node_titles(self):
        self.g.add_nodes(range(10))

        for n in self.g.nodes:
            n["title"] = "node #" + str(n["id"])

        ref = ["node #" + str(i) for i in range(10)]
        self.assertEqual(set(map(lambda s: s["title"], self.g.nodes)), set(ref))

    def test_node_sizes(self):
        self.g.add_nodes(range(10))

        for n in self.g.nodes:
            n["size"] = n["id"] * 2

        ref = [i * 2 for i in range(10)]
        self.assertEqual(set(map(lambda s: s["size"], self.g.nodes)), set(ref))

    def test_adding_nodes(self):
        g = self.g
        g.add_nodes(range(5))
        self.assertTrue(g.get_nodes(), range(5))

    def test_adding_nodes_with_props(self):
        g = self.g
        g.add_nodes(range(4), size=range(4), color=range(
            4), title=range(4), label=range(4), x=range(4), y=range(4))
        for i, n in enumerate(g.nodes):
            self.assertEqual(n["size"], i)
            self.assertEqual(n["color"], i)
            self.assertEqual(n["title"], i)
            self.assertEqual(n["label"], i)
            self.assertEqual(n["x"], i)
            self.assertEqual(n["y"], i)

    def test_labels(self):
        g = self.g
        g.add_node(0)
        self.assertTrue(g.nodes[0]["label"] == 0)
        g.add_node(50, label="NODE 50")
        self.assertTrue(g.nodes[1]["label"] == "NODE 50")

    def test_nodes_with_stringids(self):
        g = self.g
        g.add_nodes(["n1", "n2", "n3"])
        self.assertTrue(g.node_ids == ["n1", "n2", "n3"])

    def test_adj_list(self):
        g = self.g
        g.add_nodes(range(4))
        g.add_edges([(0, 1, 1), (0, 2, 1), (0, 3, 1), (1, 3, 1)])
        alist = g.get_adj_list()
        self.assertEqual(len(alist), g.num_nodes())
        self.assertEqual(alist[0], set([1, 2, 3]))
        self.assertEqual(alist[1], set([0, 3]))

    def test_neighbors(self):
        g = self.g
        g.add_nodes(range(5))
        g.add_edge(0, 1)
        g.add_edge(0, 2)
        g.add_edge(1, 3)
        g.add_edge(1, 4)
        self.assertEqual(g.neighbors(0), set([1, 2]))

    def test_length(self):
        g = self.g
        g.add_node(0)
        self.assertEqual(g.num_nodes(), 1)

    def test_get_network_data(self):
        self.assertEqual(len(self.g.get_network_data()), 6)


class EdgeTestCase(unittest.TestCase):

    def setUp(self):
        self.g = Network()
        self.g.add_nodes([0, 1, 2, 3])

    def test_non_existent_edge(self):
        self.assertRaises(AssertionError, self.g.add_edge, 5, 1)
        self.assertRaises(AssertionError, self.g.add_edge,
                          "node1", "node2")

    def test_no_edge_length(self):
        self.assertTrue(self.g.num_nodes() == 4)
        self.assertTrue(self.g.num_edges() == 0)

    def test_add_one_edge(self):
        self.g.add_edge(0, 1)
        self.assertTrue(self.g.num_edges() == 1)
        self.assertTrue({"from": 0, "to": 1} in self.g.edges)

    def test_add_two_edges_no_dups(self):
        self.g.add_edge(0, 1)
        self.g.add_edge(0, 1)
        self.assertTrue(self.g.num_edges() == 1)
        self.g.add_edge(1, 2)
        self.assertTrue(self.g.num_edges() == 2)
        self.assertEqual([{"from": 0, "to": 1},
                          {"from": 1, "to": 2}],
                         self.g.edges)

    def test_add_edges_no_weights(self):
        self.g.add_edges(
            [
                (0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)
            ]
        )
        self.assertEqual(self.g.num_edges(), 6)
        self.assertEqual(self.g.neighbors(0), set([1, 2, 3]))
        self.assertEqual(self.g.neighbors(1), set([0, 2, 3]))
        self.assertEqual(self.g.neighbors(2), set([0, 1, 3]))
        self.assertEqual(self.g.neighbors(3), set([0, 1, 2]))
        self.assertTrue("weight" not in
                        [es for es in self.g.edges])

    def test_add_edges_weights(self):
        self.g.add_edges(
            [
                (0, 1, 1), (0, 2, 2), (0, 3, 3),
                (1, 2, 4), (1, 3, 5), (2, 3, 6)
            ]
        )
        self.assertEqual(self.g.num_edges(), 6)
        self.assertEqual(self.g.neighbors(0), set([1, 2, 3]))
        self.assertEqual(self.g.neighbors(1), set([0, 2, 3]))
        self.assertEqual(self.g.neighbors(2), set([0, 1, 3]))
        self.assertEqual(self.g.neighbors(3), set([0, 1, 2]))
        for edges in self.g.edges:
            self.assertTrue("width" in edges)
        self.assertEqual(
            list([1, 2, 3, 4, 5, 6]),
            list(map(lambda x: x["width"], self.g.edges)))

    def test_add_edges_mixed_weights(self):
        self.g.add_edges(
            [
                (0, 1, 1), (0, 2), (0, 3, 3),
                (1, 2), (1, 3, 5), (2, 3)
            ]
        )
        self.assertEqual(self.g.num_edges(), 6)
        self.assertEqual(self.g.neighbors(0), set([1, 2, 3]))
        self.assertEqual(self.g.neighbors(1), set([0, 2, 3]))
        self.assertEqual(self.g.neighbors(2), set([0, 1, 3]))
        self.assertEqual(self.g.neighbors(3), set([0, 1, 2]))
        self.assertEqual(
            list([1, None, 3, None, 5, None]),
            list(map(lambda x: x.get("width", None), self.g.edges)))

    def test_add_edge_directed(self):
        self.g.directed = True
        self.g.add_edge(0, 1)
        self.assertTrue(self.g.edges)
        for e in self.g.edges:
            self.assertTrue(e["arrows"] == "to")


class UtilsTestCase(unittest.TestCase):

    def setUp(self):
        self.g = Network()
        self.g.add_nodes([0, 1, 2, 3])

    def test_html_naming(self):
        self.assertRaises(AssertionError, self.g.write_html, "4nodes.htl")
        self.assertRaises(AssertionError, self.g.write_html, "4nodes.hltm")
        self.assertRaises(AssertionError, self.g.write_html, "4nodes. htl")
        self.g.write_html("4nodes.html")
        self.assertTrue("4nodes.html" in os.listdir("."))
        os.remove("4nodes.html")


class PhysicsTestCase(unittest.TestCase):

    def setUp(self):
        self.g = Network()
        self.g.add_nodes([0, 1, 2, 3])

    def test_barnes_hut(self):
        self.g.barnes_hut()
        self.assertTrue("barnesHut" in vars(self.g.options.physics))

    def test_repulsion(self):
        self.g.repulsion()
        self.assertTrue("repulsion" in vars(self.g.options.physics))

    def test_hrepulsion(self):
        self.g.hrepulsion()
        self.assertTrue("hierarchicalRepulsion" in
                        vars(self.g.options.physics))

    def test_force_atlas_2based(self):
        self.g.force_atlas_2based()
        self.assertTrue("forceAtlas2Based" in vars(self.g.options.physics))

    def test_toggle_physics(self):
        self.assertTrue(self.g.options.physics['enabled'])
        self.g.toggle_physics(False)
        self.assertFalse(self.g.options.physics['enabled'])

    def test_stabilization(self):
        self.g.toggle_stabilization(True)
        self.assertTrue(self.g.options.physics.stabilization['enabled'])
        self.g.toggle_stabilization(False)
        self.assertFalse(self.g.options.physics.stabilization['enabled'])


class InteractionTestCase(unittest.TestCase):

    def setUp(self):
        self.g = Network()
        self.g.add_nodes([0, 1, 2, 3])

    def test_toggle_drag_nodes(self):
        self.assertTrue(self.g.options.interaction['dragNodes'])
        self.g.toggle_drag_nodes(False)
        self.assertFalse(self.g.options.interaction['dragNodes'])

    def test_toggle_hide_edges_on_drag(self):
        self.assertFalse(self.g.options.interaction['hideEdgesOnDrag'])
        self.g.toggle_hide_edges_on_drag(True)
        self.assertTrue(self.g.options.interaction['hideEdgesOnDrag'])

    def test_toggle_hide_nodes_on_drag(self):
        self.assertFalse(self.g.options.interaction['hideNodesOnDrag'])
        self.g.toggle_hide_nodes_on_drag(True)
        self.assertTrue(self.g.options.interaction['hideNodesOnDrag'])


class ConfigureTestCase(unittest.TestCase):

    def setUp(self):
        self.g = Network()
        self.g.add_nodes([0, 1, 2, 3])

    def test_show_buttons(self):
        self.assertFalse(self.g.options.configure['enabled'])
        self.g.show_buttons(True)
        self.assertTrue(self.g.options.configure['enabled'])


class EdgeOptionsTestCase(unittest.TestCase):

    def setUp(self):
        self.g = Network()
        self.g.add_nodes([0, 1, 2, 3])

    def test_set_edge_smooth(self):
        self.assertEqual(self.g.options.edges.smooth.type, 'continuous')
        self.g.set_edge_smooth('dynamic')
        self.assertEqual(self.g.options.edges.smooth.type, 'dynamic')

    def test_inherit_colors(self):
        self.assertTrue(self.g.options.edges.color.inherit)
        self.g.inherit_edge_colors(False)
        self.assertFalse(self.g.options.edges.color.inherit)


class LayoutTestCase(unittest.TestCase):

    def setUp(self):
        self.g = Network(layout=True)

    def test_can_enable_init(self):
        self.assertTrue(self.g.options['layout'])
    
    def test_layout_disabled(self):
        self.g = Network()
        self.assertRaises(KeyError, lambda: self.g.options['layout'])
    
    def test_levelSeparation(self):
        self.assertTrue(self.g.options.layout.hierarchical.levelSeparation)
    
    def test_treeSpacing(self):
        self.assertTrue(self.g.options.layout.hierarchical.treeSpacing)
    
    def test_blockShifting(self):
        self.assertTrue(self.g.options.layout.hierarchical.blockShifting)
    
    def test_edgeMinimization(self):
        self.assertTrue(self.g.options.layout.hierarchical.edgeMinimization)
    
    def test_parentCentralization(self):
        self.assertTrue(self.g.options.layout.hierarchical.parentCentralization)

    def test_sortMethod(self):
        self.assertTrue(self.g.options.layout.hierarchical.sortMethod)

    def test_set_edge_minimization(self):
        self.g.options.layout.set_separation(10)
        self.assertTrue(self.g.options.layout.hierarchical.levelSeparation == 10)
    
    def test_set_tree_spacing(self):
        self.g.options.layout.set_tree_spacing(10)
        self.assertTrue(self.g.options.layout.hierarchical.treeSpacing == 10)

    def test_set_edge_minimization(self):
        self.g.options.layout.set_edge_minimization(True)
        self.assertTrue(self.g.options.layout.hierarchical.edgeMinimization == True)
        self.g.options.layout.set_edge_minimization(False)
        self.assertTrue(self.g.options.layout.hierarchical.edgeMinimization == False)

        

    
