class Node(object):

    def __init__(self, n_id, shape, label, **opts):
        self.options = opts
        self.options["id"] = n_id
        self.options["label"] = label
        self.options["shape"] = shape
