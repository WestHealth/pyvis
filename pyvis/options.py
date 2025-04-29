from .physics import *

class EdgeOptions(object):
    """
    This is where the construction of the edges' options takes place.
    So far, the edge smoothness can be switched through this object
    as well as the edge color's inheritance. 
    """

    def __init__(self):
        self.smooth = self.Smooth()
        self.color = self.Color()

    def inherit_colors(self, status):
        """
        Whether or not to inherit colors from the source node.
        If this is set to `from` then the edge will take the color
        of the source node. If it is set to `to` then the color will
        be that of the destination node.

        .. note:: If set to `True` then the `from` behavior is adopted
                  and vice versa.
        """
        self.color.inherit = status

    def toggle_smoothness(self, smooth_type):
        """
        Change smooth option for edges. When using dynamic, the edges will
        have an invisible support node guiding the shape. This node is part
        of the physics simulation,

        :param smooth_type: Possible options are dynamic, continuous, discrete,
                            diagonalCross, straightCross, horizontal, vertical,
                            curvedCW, curvedCCW, cubicBezier
        
        :type smooth_type: str
        """
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
            self.enabled = True
            self.type = "dynamic"

    class Color(object):
        """
        The color object contains the color information of the edge
        in every situation. When the edge only needs a single color value
        like 'rgb(120,32,14)', '#ffffff' or 'red' can be supplied instead
        of an object.
        """
        def __repr__(self):
            return str(self.__dict__)

        def __init__(self):
            self.inherit = True

    
class Interaction(object):
    """
    Used for all user interaction with the network. Handles mouse
    and touch events as well as the navigation buttons and the popups.
    """
    def __repr__(self):
        return str(self.__dict__)

    def __init__(self):
        self.hideEdgesOnDrag = False
        self.hideNodesOnDrag = False
        self.dragNodes = True

    def __getitem__(self, item):
        return self.__dict__[item]


class Configure(object):
    """
    Handles the HTML part of the canvas and generates
    an interactive option editor with filtering.
    """

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
            self.randomSeed = randomSeed
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
    """
    Represents the global options of the network.
    This object consists of indiviual sub-objects
    that map to VisJS's modules of:
        - configure
        - layout
        - interaction
        - physics
        - edges
    
    The JSON representation of this object is directly passed
    in to the VisJS framework.
    In the future this can be expanded to completely mimic
    the structure VisJS can expect.
    """
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

    def set(self, new_options):
        """
        This method should accept a JSON string and replace its internal
        options structure with the given argument after parsing it.
        In practice, this method should be called after using the browser
        to experiment with different physics and layout options, using
        the generated JSON options structure that is spit out from the
        front end to serve as input to this method as a string.

        :param new_options: The JSON like string of the options that will
                            override.
        
        :type new_options: str
        """
        
        def del_nulls(prop_dict):
            for key in list(prop_dict.keys()):
                if (prop_dict[key] == None):
                        prop_dict.pop(key)
                elif isinstance(prop_dict[key], dict):
                        del_nulls(prop_dict[key])
            return prop_dict

        def deep_merge(dict1, dict2):
            merged_dict=dict1
            
            for key in dict2:
                if (key in dict1) and isinstance(dict1[key], dict) and isinstance(dict2[key], dict):
                    merged_dict[key] = deep_merge(dict1[key], dict2[key])
                else:
                    merged_dict[key] = dict2[key]
            return merged_dict

        new_options = new_options.replace("\n", "").replace(" ", "")
        first_bracket = new_options.find("{")
        new_options = new_options[first_bracket:]
        new_options = json.loads(new_options)
        new_options = del_nulls(new_options)
        
        current_options = self.to_json()
        current_options = json.loads(current_options)
        
        options_to_set = deep_merge(current_options, new_options)
        return options_to_set
        

    def to_json(self):
        return json.dumps(
            self, default=lambda o: o.__dict__,
            sort_keys=True, indent=4)
