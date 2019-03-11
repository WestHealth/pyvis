from .physics import *

class EdgeOptions(object):

    def __init__(self):
        self.smooth = self.Smooth()
        self.color = self.Color()

    def inherit_colors(self, status):
        self.color.inherit = status

    def toggle_smoothness(self, smooth_type):
        self.smooth.type = smooth_type

    def __repr__(self):
        return str(self.__dict__)

    class Smooth(object):
        """
        When the edges are made to be smooth, the edges are drawn as a
        dynamic quadratic bezier curve. The drawing of these curves
        takes longer than that of the straight curves but it looks better.
        There is a difference between dynamic smooth curves and static
        smooth curves. The dynamic smooth curves have an invisible support
        node that takes part in the physics simulation. If there are a lot
        of edges, another kind of smooth than dynamic would be better for
        performance.
        """
        def __repr__(self):
            return str(self.__dict__)

        def __init__(self):
            self.enabled = False
            self.type = "continuous"

    class Color(object):
        """
        The color object contains the color information of the edge
        in every situation. When the edge only needs a sngle color value
        like 'rgb(120,32,14)', '#ffffff' or 'red' can be supplied instead
        of an object.
        """
        def __repr__(self):
            return str(self.__dict__)

        def __init__(self):
            self.inherit = True

    
class Interaction(object):

    def __repr__(self):
        return str(self.__dict__)

    def __init__(self):
        self.hideEdgesOnDrag = False
        self.hideNodesOnDrag = False
        self.dragNodes = True

    def __getitem__(self, item):
        return self.__dict__[item]


class Configure(object):

    def __repr__(self):
        return str(self.__dict__)

    def __init__(self, enabled=False, filter_=None):
        self.enabled = enabled
        if filter_:
            self.filter = filter_ 

    def __getitem__(self, item):
        return self.__dict__[item]


class Layout(object):
    """
    Acts as the camera that looks on the canvas.
    Does the animation, zooming and focusing.
    """
    
    def __repr__(self):
        return str(self.__dict__)

    def __init__(self, randomSeed=None, improvedLayout=True):
            if not randomSeed:
                self.randomSeed = 0
            else:
                self.radnomSeed = randomSeed
            self.improvedLayout = improvedLayout
            self.hierarchical = self.Hierarchical(enabled=True)
    
    def set_separation(self, distance):
        """
        The distance between the different levels.
        """
        self.hierarchical.levelSeparation = distance
    
    def set_tree_spacing(self, distance):
        """
        Distance between different trees (independent networks). This is
        only for the initial layout. If you enable physics, the repulsion
        model will denote the distance between the trees.
        """
        self.hierarchical.treeSpacing = distance

    def set_edge_minimization(self, status):
        """
        Method for reducing whitespace. Can be used alone or together with
        block shifting. Enabling block shifting will usually speed up the
        layout process. Each node will try to move along its free axis to
        reduce the total length of it's edges. This is mainly for the
        initial layout. If you enable physics, they layout will be determined
        by the physics. This will greatly speed up the stabilization time
        """
        self.hierarchical.edgeMinimization = status

    class Hierarchical(object):

        def __getitem__(self, item):
            return self.__dict__[item]

        def __init__(self,
                    enabled=False,
                    levelSeparation=150,
                    treeSpacing=200,
                    blockShifting=True,
                    edgeMinimization=True,
                    parentCentralization=True,
                    sortMethod='hubsize'):

            self.enabled = enabled
            self.levelSeparation = levelSeparation
            self.treeSpacing = treeSpacing
            self.blockShifting = blockShifting
            self.edgeMinimization = edgeMinimization
            self.parentCentralization = parentCentralization
            self.sortMethod = sortMethod

    

class Options(object):

    def __repr__(self):
        return str(self.__dict__)

    def __getitem__(self, item):
        return self.__dict__[item]

    def __init__(self, layout=None):
        if layout:
            self.layout = Layout()
        self.interaction = Interaction()
        self.configure = Configure()
        self.physics = Physics()
        self.edges = EdgeOptions()

    def to_json(self):
        return json.dumps(
            self, default=lambda o: o.__dict__,
            sort_keys=True, indent=4)
