import json


class Physics(object):

    engine_chosen = False

    def __getitem__(self, item):
        return self.__dict__[item]
    
    def __repr__(self):
        return str(self.__dict__)

    class barnesHut(object):
        """
        BarnesHut is a quadtree based gravity model.
        This is the fastest, default and recommended.
        """

        def __init__(self, params):
            self.gravitationalConstant = params["gravity"]
            self.centralGravity = params["central_gravity"]
            self.springLength = params["spring_length"]
            self.springConstant = params["spring_strength"]
            self.damping = params["damping"]
            self.avoidOverlap = params["overlap"]


    class forceAtlas2Based(object):
        """
        Force Atlas 2 has been develoved by Jacomi et all (2014)
        for use with Gephi. The force Atlas based solver makes use
        of some of the equations provided by them and makes use of
        some of the barnesHut implementation in vis. The Main differences
        are the central gravity model, which is here distance independent,
        and repulsion being linear instead of quadratic. Finally, all node
        masses have a multiplier based on the amount of connected edges
        plus one.
        """
        def __init__(self, params):
            self.gravitationalConstant = params["gravity"]
            self.centralGravity = params["central_gravity"]
            self.springLength = params["spring_length"]
            self.springConstant = params["spring_strength"]
            self.damping = params["damping"]
            self.avoidOverlap = params["overlap"]

    class Repulsion(object):
        """
        The repulsion model assumes nodes have a simplified field
        around them. Its force lineraly decreases from 1
        (at 0.5*nodeDistace and smaller) to 0 (at 2*nodeDistance)
        """
        def __init__(self, params):
            self.nodeDistance = params['node_distance']
            self.centralGravity = params['central_gravity']
            self.springLength = params['spring_length']
            self.springConstant = params['spring_strength']
            self.damping = params['damping']

    class hierarchicalRepulsion(object):
        """
        This model is based on the repulsion solver but the levels
        are taken into accound and the forces
        are normalized.
        """
        def __init__(self, params):
            self.nodeDistance = params['node_distance']
            self.centralGravity = params['central_gravity']
            self.springLength = params['spring_length']
            self.springConstant = params['spring_strength']
            self.damping = params['damping']

    class Stabilization(object):
        """
        This makes the network stabilized on load using default settings.
        """
        def __getitem__(self, item):
            return self.__dict__[item]

        def __init__(self):
            self.enabled = True
            self.iterations = 1000
            self.updateInterval = 50
            self.onlyDynamicEdges = False
            self.fit = True

        def toggle_stabilization(self, status):
            self.enabled = status

    def __init__(self):
        self.enabled = True
        self.stabilization = self.Stabilization()

    def use_barnes_hut(self, params):
        self.barnesHut = self.barnesHut(params)

    def use_force_atlas_2based(self, params):
        self.forceAtlas2Based = self.forceAtlas2Based(params)
        self.solver = 'forceAtlas2Based'

    def use_repulsion(self, params):
        self.repulsion = self.Repulsion(params)
        self.solver = 'repulsion'

    def use_hrepulsion(self, params):
        self.hierarchicalRepulsion = self.hierarchicalRepulsion(params)
        self.solver = 'hierarchicalRepulsion'

    def toggle_stabilization(self, status):
        self.stabilization.toggle_stabilization(status)

    def to_json(self):
        return json.dumps(
            self, default=lambda o: o.__dict__,
            sort_keys=True, indent=4)
