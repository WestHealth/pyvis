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



class Options(object):

    def __repr__(self):
        return str(self.__dict__)

    def __init__(self):
        # self.layout = Layout()
        self.interaction = Interaction()
        self.configure = Configure()
        self.physics = Physics()
        self.edges = EdgeOptions()

    def to_json(self):
        return json.dumps(
            self, default=lambda o: o.__dict__,
            sort_keys=True, indent=4)
