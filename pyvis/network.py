from .node import Node
from .edge import Edge
from .options import Options, Configure
from .utils import check_html
from jinja2 import Template
import webbrowser
from IPython.display import IFrame
from IPython.core.display import HTML
from collections import defaultdict
import networkx as nx
import json
import os


class Network(object):
    """
    The Network class is the focus of this library. All viz functionality
    should be implemented off of a Network instance.

    To instantiate:

    >>> nt = Network()
    """

    def __init__(self,
                 height="500px",
                 width="500px",
                 directed=False,
                 notebook=False,
                 bgcolor="#ffffff",
                 font_color=False):
        """
        :param height: The height of the canvas
        :param width: The width of the canvas
        :param directed: Whether or not to use a directed graph. This is false
                         by default.
        :param notebook: True if using jupyter notebook.
        :param bgcolor: The background color of the canvas.
        :font_color: The color of the node labels text

        :type height: num or str
        :type width: num or str
        :type directed: bool
        :type notebook: bool
        :type bgcolor: str
        :type font_color: str
        """
        self.nodes = []
        self.edges = []
        self.height = height
        self.width = width
        self.html = ""
        self.shape = "dot"
        self.font_color = font_color
        self.directed = directed
        self.bgcolor = bgcolor
        self.use_DOT = False
        self.dot_lang = ""
        self.options = Options()
        self.widget = False
        self.node_ids = []
        self.template = None
        self.conf = False
        self.path = os.path.dirname(__file__) + "/templates/template.html"
        
        if notebook:
            self.prep_notebook()
            
    def __str__(self):
        """
        override print to show readable graph data
        """
        return str(
            json.dumps(
                {
                    "Nodes": self.node_ids,
                    "Edges": self.edges,
                    "Height": self.height,
                    "Width": self.width
                },
                indent=4
            )
        )

    def __repr__(self):
        return '{} |N|={} |E|={:,}'.format(
            self.__class__, self.num_nodes(), self.num_edges()
        )

    def add_node(self, n_id, label=None, shape="dot", **options):
        """
        This method adds a node to the network, given a mandatory node ID.
        Node labels default to node ids if no label is specified during the
        call.

        >>> nt = Network("500px", "500px")
        >>> nt.add_node(0, label="Node 0")
        >>> nt.add_node(1, label="Node 1", color = "blue")

        :param n_id: The id of the node. The id is mandatory for nodes and
                     they have to be unique. This should obviously be set per
                     node, not globally.

        :param label: The label is the piece of text shown in or under the
                      node, depending on the shape.

        :param borderWidth:	The width of the border of the node.

        :param borderWidthSelected:	The width of the border of the node when
                                    it is selected. When undefined, the
                                    borderWidth * 2 is used.

        :param brokenImage:	When the shape is set to image or circularImage,
                            this option can be an URL to a backup image in
                            case the URL supplied in the image option cannot
                            be resolved.

        :param group: When not undefined, the node will belong to the defined
                      group. Styling information of that group will apply to
                      this node. Node specific styling overrides group styling.

        :param hidden: When true, the node will not be shown. It will still be
                       part of the physics simulation though!

        :param image: When the shape is set to image or circularImage, this
                      option should be the URL to an image. If the image
                      cannot be found, the brokenImage option can be used.

        :param labelHighlightBold: Determines whether or not the label becomes
                                   bold when the node is selected.

        :param level: When using the hierarchical layout, the level determines
                      where the node is going to be positioned.

        :param mass: The barnesHut physics model (which is enabled by default)
                     is based on an inverted gravity model. By increasing
                     the mass of a node, you increase it's repulsion. Values
                     lower than 1 are not recommended.

        :param physics:	When false, the node is not part of the physics
                        simulation. It will not move except for from
                        manual dragging.

        :param shape: The shape defines what the node looks like. There are
                      two types of nodes. One type has the label inside of
                      it and the other type has the label underneath it. The
                      types with the label inside of it are: ellipse, circle,
                      database, box, text. The ones with the label outside of
                      it are: image, circularImage, diamond, dot, star,
                      triangle, triangleDown, square and icon.

        :param size: The size is used to determine the size of node shapes that
                     do not have the label inside of them. These shapes are:
                     image, circularImage, diamond, dot, star, triangle,
                     triangleDown, square and icon.

        :param title: Title to be displayed when the user hovers over the node.
                      The title can be an HTML element or a string containing
                      plain text or HTML.

        :param value: When a value is set, the nodes will be scaled using the
                      options in the scaling object defined above.

        :param x: This gives a node an initial x position. When using the
                  hierarchical layout, either the x or y position is set by the
                  layout engine depending on the type of view. The other value
                  remains untouched. When using stabilization, the stabilized
                  position may be different from the initial one. To lock the
                  node to that position use the physics or fixed options.

        :param y: This gives a node an initial y position. When using the
                  hierarchical layout,either the x or y position is set by
                  the layout engine depending on the type of view. The
                  other value remains untouched. When using stabilization,
                  the stabilized position may be different from the initial
                  one. To lock the node to that position use the physics or
                  fixed options.

        :type n_id: str or int
        :type label: str or int
        :type borderWidth: num (optional)
        :type borderWidthSelected: num (optional)
        :type brokenImage: str (optional)
        :type group: str (optional)
        :type hidden: bool (optional)
        :type image: str (optional)
        :type labelHighlightBold: bool (optional)
        :type level: num (optional)
        :type mass: num (optional)
        :type physics: bool (optional)
        :type shape: str (optional)
        :type size: num (optional)
        :type title: str or html element (optional)
        :type value: num (optional)
        :type x: num (optional)
        :type y: num (optional)
        """
        assert isinstance(n_id, str) or isinstance(n_id, int)
        if label:
            node_label = label
        else:
            node_label = n_id
        if n_id not in self.node_ids:
            n = Node(n_id, shape, label=node_label, font_color=self.font_color, **options)
            self.nodes.append(n.options)
            self.node_ids.append(n_id)

    def add_nodes(self, nodes, **kwargs):
        """
        This method adds multiple nodes to the network from a list.
        Default behavior uses values of 'nodes' for node ID and node label
        properties. You can also specify other lists of properties to go
        along each node.

        Example:

        >>> g = net.Network()
        >>> g.add_nodes([1, 2, 3], size=[2, 4, 6], title=["n1", "n2", "n3"])
        >>> g.nodes
        >>> [{'id': 1, 'label': 1, 'shape': 'dot', 'size': 2, 'title': 'n1'},

        Output:

        >>> {'id': 2, 'label': 2, 'shape': 'dot', 'size': 4, 'title': 'n2'},
        >>> {'id': 3, 'label': 3, 'shape': 'dot', 'size': 6, 'title': 'n3'}]


        :param nodes: A list of nodes.

        :type nodes: list
        """
        valid_args = ["size", "value", "title", "x", "y", "label", "color"]
        for k in kwargs:
            assert k in valid_args, "invalid arg '" + k + "'"

        nd = defaultdict(dict)
        for i in range(len(nodes)):
            for k, v in kwargs.items():
                assert(
                    len(v) == len(nodes)
                ), "keyword arg %s [length %s] does not match" \
                   "[length %s] of nodes" % \
                   (
                    k, len(v), len(nodes)
                )
                nd[nodes[i]].update({k: v[i]})

        for node in nodes:
            assert isinstance(node, int) or isinstance(node, str)
            self.add_node(node, **nd[node])

    def num_nodes(self):
        """
        Return number of nodes

        :returns: :py:class:`int`
        """
        return len(self.node_ids)

    def num_edges(self):
        """
        Return number of edges

        :returns: :py:class:`int`
        """
        return len(self.edges)

    def add_edge(self, source, to, **options):
        """

        Adding edges is done based off of the IDs of the nodes. Order does
        not matter unless dealing with a directed graph.

        >>> nt.add_edge(0, 1) # adds an edge from node ID 0 to node ID
        >>> nt.add_edge(0, 1, value = 4) # adds an edge with a width of 4


        :param arrowStrikethrough: When false, the edge stops at the arrow.
                                   This can be useful if you have thick lines
                                   and you want the arrow to end in a point.
                                   Middle arrows are not affected by this.

        :param from: Edges are between two nodes, one to and one from. This
                     is where you define the from node. You have to supply
                     the corresponding node ID. This naturally only applies
                     to individual edges.

        :param hidden: When true, the edge is not drawn. It is part still part
                       of the physics simulation however!

        :param physics:	When true, the edge is part of the physics simulation.
                        When false, it will not act as a spring.

        :param title: The title is shown in a pop-up when the mouse moves over
                      the edge.

        :param to: Edges are between two nodes, one to and one from. This is
                   where you define the to node. You have to supply the
                   corresponding node ID. This naturally only applies to
                   individual edges.

        :param value: When a value is set, the edges' width will be scaled
                      using the options in the scaling object defined above.

        :param width: The width of the edge. If value is set, this is not used.


        :type arrowStrikethrough: bool
        :type from: str or num
        :type hidden: bool
        :type physics: bool
        :type title: str
        :type to: str or num
        :type value: num
        :type width: num
        """
        edge_exists = False

        # verify nodes exists
        assert source in self.get_nodes(), \
            "non existent node '" + str(source) + "'"

        assert to in self.get_nodes(), \
            "non existent node '" + str(to) + "'"

        # we only check existing edge for undirected graphs
        if not self.directed:
            for e in self.edges:
                frm = e['from']
                dest = e['to']
                if (
                    (source == dest and to == frm) or
                    (source == frm and to == dest)
                ):
                    # edge already exists
                    edge_exists = True

        if not edge_exists:
            e = Edge(source, to, self.directed, **options)
            self.edges.append(e.options)

    def add_edges(self, edges):
        """
        This method serves to add multiple edges between existing nodes
        in the network instance. Adding of the edges is done based off
        of the IDs of the nodes. Order does not matter unless dealing with a
        directed graph.

        :param edges: A list of tuples, each tuple consists of source of edge,
                      edge destination and and optional width.

        :type arrowStrikethrough: list of tuples
        """
        for edge in edges:
            # if incoming tuple contains a weight
            if len(edge) == 3:
                self.add_edge(edge[0], edge[1], width=edge[2])
            else:
                self.add_edge(edge[0], edge[1])

    def get_network_data(self):
        """
        Extract relevant information about this network in order to inject into
        a Jinja2 template.

        Returns:
                nodes (list), edges (list), height (
                    string), width (string), options (object)

        Usage:

        >>> nodes, edges, height, width, options = net.get_network_data()
        """
        return (self.nodes, self.edges, self.height,
                self.width, self.options.to_json())

    def save_graph(self, name):
        """
        Save the graph as html in the current directory with name.

        :param name: the name of the html file to save as
        :type name: str
        """
        check_html(name)
        self.write_html(name)

    def write_html(self, name, notebook=False):
        """
        This method gets the data structures supporting the nodes, edges,
        and options and updates the template to write the HTML holding
        the visualization.

        :type name_html: str
        """
        check_html(name)
        # here, check if an href is present in the hover data
        use_link_template = False
        for n in self.nodes:
            title = n.get("title", None)
            if title:
                if "href" in title:
                    """
                    this tells the template to override default hover
                    mechanic, as the tooltip would move with the mouse
                    cursor which made interacting with hover data useless.
                    """
                    use_link_template = True
                    break
        if not notebook:
            with open(self.path) as html:
                content = html.read()
            template = Template(content)
        else:
            template = self.template

        nodes, edges, height, width, options = self.get_network_data()
        self.html = template.render(height=height,
                                    width=width,
                                    nodes=nodes,
                                    edges=edges,
                                    options=options,
                                    use_DOT=self.use_DOT,
                                    dot_lang=self.dot_lang,
                                    widget=self.widget,
                                    bgcolor=self.bgcolor,
                                    conf=self.conf,
                                    tooltip_link=use_link_template)

        with open(name, "w+") as out:
            out.write(self.html)

        if notebook:
            return IFrame(name, width=self.width, height=self.height)

    def show(self, name):
        """
        Writes a static HTML file and saves it locally before opening.

        :param: name: the name of the html file to save as
        :type name: str
        """
        check_html(name)
        if self.template is not None:
            return self.write_html(name, notebook=True)
        else:
            self.write_html(name)
            webbrowser.open(name)

    def prep_notebook(self,
                      custom_template=False, custom_template_path=None):
        """
        Loads the template data into the template attribute of the network.
        This should be done in a jupyter notebook environment before showing
        the network.

        Example:
                >>> net.prep_notebook()
                >>> net.show("nb.html")


        :param path: the relative path pointing to a template html file
        :type path: string
        """
        if custom_template and custom_template_path:
            self.set_template(custom_template_path)
        with open(self.path) as html:
            content = html.read()
        self.template = Template(content)

    def set_template(self, path_to_template):
        self.path = path_to_template

    def from_DOT(self, dot):
        """
        This method takes the contents of .DOT file and converts it
        to a PyVis visualization.

        Assuming the contents of test.dot contains:
        digraph sample3 {
        A -> {B ; C ; D}
        C -> {B ; A}
        }

        Usage:

        >>> nt.Network("500px", "500px")
        >>> nt.from_DOT("test.dot")
        >>> nt.show("dot.html")

        :param dot: The path of the dotfile being converted.
        :type dot: .dot file

        """
        self.use_DOT = True
        file = open(dot, "r")
        s = str(file.read())
        self.dot_lang = " ".join(s.splitlines())
        self.dot_lang = self.dot_lang.replace('"', '\\"')

    def get_adj_list(self):
        """
        This method returns the user an adjacency list representation
        of the network.

        :returns: dictionary mapping of Node ID to list of Node IDs it
        is connected to.
        """
        a_list = {}
        for i in self.nodes:
            a_list[i["id"]] = set()
        if self.directed:
            for e in self.edges:
                source = e["from"]
                dest = e["to"]
                a_list[source].add(dest)
        else:
            for e in self.edges:
                source = e["from"]
                dest = e["to"]
                if dest not in a_list[source] and source not in a_list[dest]:
                    a_list[source].add(dest)
                    a_list[dest].add(source)
        return a_list

    def neighbors(self, node):
        """
        Given a node id, return the set of neighbors of this particular node.

        :param node: The node to get the neighbors from
        :type node: str or int

        :returns: set
        """
        assert(isinstance(node, str) or isinstance(node, int)
               ), "error: expected int or str for node but got %s" % type(node)
        assert(node in self.node_ids), "error: %s node not in network" % node
        return self.get_adj_list()[node]

    def from_nx(self, nx_graph):
        """
        This method takes an exisitng Networkx graph and translates
        it to a PyVis graph format that can be accepted by the VisJs
        API in the Jinja2 template. This operation is done in place.

        :param nx_graph: The Networkx graph object that is to be translated.
        :type nx_graph: networkx.Graph instance
        >>> nx_graph = Networkx.cycle_graph()
        >>> nt = Network("500px", "500px")
        # populates the nodes and edges data structures
        >>> nt.from_nx(nx_graph)
        >>> nt.show("nx.html")
        """
        assert(isinstance(nx_graph, nx.Graph))
        edges = nx_graph.edges(data=True)
        nodes = nx_graph.nodes()
        if len(edges) > 0:
            for e in edges:
                self.add_node(e[0], e[0], title=str(e[0]))
                self.add_node(e[1], e[1], title=str(e[1]))
                self.add_edge(e[0], e[1])
        else:
            self.add_nodes(nodes)

    def get_nodes(self):
        """
        This method returns an iterable list of node ids

        :returns: list
        """
        return self.node_ids

    def get_edges(self):
        """
        This method returns an iterable list of edge objects

        :returns: list
        """
        return self.edges

    def barnes_hut(
        self,
        gravity=-80000,
        central_gravity=0.3,
        spring_length=250,
        spring_strength=0.001,
        damping=0.09,
        overlap=0
    ):
        """
        BarnesHut is a quadtree based gravity model. It is the fastest. default
        and recommended solver for non-heirarchical layouts.

        :param gravity: The more negative the gravity value is, the stronger the
                        repulsion is.
        :param central_gravity: The gravity attractor to pull the entire network
                                to the center. 
        :param spring_length: The rest length of the edges
        :param spring_strength: The strong the edges springs are
        :param damping: A value ranging from 0 to 1 of how much of the velocity
                        from the previous physics simulation iteration carries
                        over to the next iteration.
        :param overlap: When larger than 0, the size of the node is taken into
                        account. The distance will be calculated from the radius
                        of the encompassing circle of the node for both the
                        gravity model. Value 1 is maximum overlap avoidance.

        :type gravity: int
        :type central_gravity: float
        :type spring_length: int
        :type spring_strength: float
        :type damping: float
        :type overlap: float
        """
        self.options.physics.use_barnes_hut(locals())

    def repulsion(
        self,
        node_distance=100,
        central_gravity=0.2,
        spring_length=200,
        spring_strength=0.05,
        damping=0.09
    ):
        """
        Set the physics attribute of the entire network to repulsion.
        When called, it sets the solver attribute of physics to repulsion.

        :param node_distance: This is the range of influence for the repulsion.
        :param central_gravity: The gravity attractor to pull the entire network
                                to the center.
        :param spring_length: The rest length of the edges
        :param spring_strength: The strong the edges springs are
        :param damping: A value ranging from 0 to 1 of how much of the velocity
                        from the previous physics simulation iteration carries
                        over to the next iteration.

        :type node_distance: int
        :type central_gravity float
        :type spring_length: int
        :type spring_strength: float
        :type damping: float
        """
        self.options.physics.use_repulsion(locals())

    def hrepulsion(
        self,
        node_distance=120,
        central_gravity=0.0,
        spring_length=100,
        spring_strength=0.01,
        damping=0.09
    ):
        """
        This model is based on the repulsion solver but the levels are
        taken into account and the forces are normalized.

        :param node_distance: This is the range of influence for the repulsion.
        :param central_gravity: The gravity attractor to pull the entire network
                                to the center.
        :param spring_length: The rest length of the edges
        :param spring_strength: The strong the edges springs are
        :param damping: A value ranging from 0 to 1 of how much of the velocity
                        from the previous physics simulation iteration carries
                        over to the next iteration.

        :type node_distance: int
        :type central_gravity float
        :type spring_length: int
        :type spring_strength: float
        :type damping: float
        """
        self.options.physics.use_hrepulsion(locals())

    def force_atlas_2based(
        self,
        gravity=-50,
        central_gravity=0.01,
        spring_length=100,
        spring_strength=0.08,
        damping=0.4,
        overlap=0
    ):
        """
        The forceAtlas2Based solver makes use of some of the equations provided
        by them and makes use of the barnesHut implementation in vis. The main
        differences are the central gravity model, which is here distance
        independent, and the repulsion being linear instead of quadratic. Finally,
        all node masses have a multiplier based on the amount of connected edges
        plus one.

        :param gravity: The more negative the gravity value is, the stronger the
                        repulsion is.
        :param central_gravity: The gravity attractor to pull the entire network
                                to the center. 
        :param spring_length: The rest length of the edges
        :param spring_strength: The strong the edges springs are
        :param damping: A value ranging from 0 to 1 of how much of the velocity
                        from the previous physics simulation iteration carries
                        over to the next iteration.
        :param overlap: When larger than 0, the size of the node is taken into
                        account. The distance will be calculated from the radius
                        of the encompassing circle of the node for both the
                        gravity model. Value 1 is maximum overlap avoidance.

        :type gravity: int
        :type central_gravity: float
        :type spring_length: int
        :type spring_strength: float
        :type damping: float
        :type overlap: float
        """
        self.options.physics.use_force_atlas_2based(locals())

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_edge_smooth(self, smooth_type):
        """
        Sets the smooth.type attribute of the edges.

        :param smooth_type: Possible options: 'dynamic', 'continuous',
                            'discrete', 'diagonalCross', 'straightCross',
                            'horizontal', 'vertical', 'curvedCW',
                            'curvedCCW', 'cubicBezier'.
                            When using dynamic, the edges will have an
                            invisible support node guiding the shape.
                            This node is part of the physics simulation.
                            Default is set to continous.

        :type smooth_type: string
        """
        self.options.edges.smooth.enabled = True
        self.options.edges.smooth.type = smooth_type

    def toggle_hide_edges_on_drag(self, status):
        """
        Displays or hides edges while dragging the network. This makes
        panning of the network easy.

        :param status: True if edges should be hidden on drag
        
        :type status: bool
        """
        self.options.interaction.hideEdgesOnDrag = status

    def toggle_hide_nodes_on_drag(self, status):
        """
        Displays or hides nodes while dragging the network. This makes
        panning of the network easy.

        :param status: When set to True, the nodes will hide on drag.
                       Default is set to False.

        :type status: bool
        """
        self.options.interaction.hideNodesOnDrag = status

    def inherit_edge_colors_from(self, status):
        """
        Edges take on the color of the node they are coming from.

        :param status: True if edges should adopt color coming from.
        :type status: bool
        """
        self.options.edges.inherit_colors(status)

    def show_buttons(self, filter_=None):
        """
        Displays or hides certain widgets to dynamically modify the
        network.

        Usage:
        >>> g.toggle_buttons(filter_=['nodes', 'edges', 'physics'])

        :param status: When set to True, the widgets will be shown.
                       Default is set to False.
        :param filter_: Only include widgets specified by `filter_`.
                        Valid options: True (gives all widgets)
                                       List of `nodes`, `edges`,
                                       `layout`, `interaction`,
                                       `manipulation`, `physics`,
                                       `selection`, `renderer`.

        :type status: bool
        :type filter_: bool or list:
        """
        self.conf = True
        self.options.configure = Configure(enabled=True, filter_=filter_)        
        self.widget = True

    def toggle_physics(self, status):
        """
        Displays or hides certain widgets to dynamically modify the
        network.

        :param status: When set to True, the widgets will be shown.
                       Default is set to False.

        :type status: bool
        """
        self.options.physics.enabled = status

    def toggle_drag_nodes(self, status):
        """
        Toggles the dragging of the nodes in the network.

        :param status: When set to True, the nodes can be dragged around
                       in the network. Default is set to False.

        :type status: bool
        """
        self.options.interaction.dragNodes = status

    def toggle_stabilization(self, status):
        """
        Toggles the stablization of the network.

        :param status: Default is set to True.

        :type status: bool
        """
        self.options.physics.toggle_stabilization(status)
