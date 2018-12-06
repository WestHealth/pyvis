class Edge(object):

    def __init__(self, source, dest, directed=False, **options):
        self.options = options
        self.options['from'] = source
        self.options['to'] = dest
        if directed:
            self.options["arrows"] = "to"
