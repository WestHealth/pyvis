class Node(object):

    def __init__(self, n_id, shape, label, font_color=False, **opts):
        self.options = opts
        self.options["id"] = n_id
        self.options["label"] = label
        self.options["shape"] = shape
        if font_color:
            self.options["font"] = dict(color=font_color)
