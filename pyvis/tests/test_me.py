import numpy as np

from ..network import Network


def test_canvas_size():
    """
    Test the canvas size
    """
    net = Network(500, 500)
    assert(net.width == 500 and net.height == 500)


def test_add_node():
    """
    Test adding a node to the network.
    """
    net = Network()

    net.add_node(0, "Test")

    assert("Test" in net.nodes[0].values())


def test_add_ten_nodes():
    """
    Test adding multiple nodes to this network
    """
    net = Network()

    for i in range(10):
        net.add_node(i, "Test " + str(i))

    assert(len(net.nodes) == 10)


def test_add_nodes_with_options():
    """
    Test adding nodes with different options
    """
    net = Network()

    sizes = [10, 20, 30]

    net.add_node(0, "Node 0", color="green", size=10)
    net.add_node(1, "Node 1", color="blue", size=20)
    net.add_node(2, "Node 2", color="yellow", size=30)

    assert(sizes[node["id"]] == node["size"] for node in net.nodes)


def test_add_edge():
    """
    Test adding an edge between nodes
    """

    net = Network()

    for i in range(10):
        net.add_node(i, "Node " + str(i))

    net.add_edge(0, 1)
    net.add_edge(0, 2)
    net.add_edge(0, 3)
    net.add_edge(0, 4)
    net.add_edge(0, 5)
    net.add_edge(0, 6)
    net.add_edge(0, 7)
    net.add_edge(0, 8)
    net.add_edge(0, 9)

    assert(net.get_adj_list()[0] == set([2, 1, 3, 4, 5, 6, 7, 8, 9]))

def test_add_numpy_nodes():
    """
    Test adding numpy array nodes since these
    nodes will have specific numpy types
    """
    arrayNodes = np.array([1,2,3,4])
    g = Network()
    g.add_nodes(np.array([1,2,3,4]))
    assert g.get_nodes() == [1,2,3,4]
