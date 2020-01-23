from skeletor import graph
from gremlin_python.process.graph_traversal import GraphTraversalSource


class GraphModel(object):
    g: GraphTraversalSource = None

    def __init__(self, *args, **kwargs):
        self.g = graph.get_traversal()
        pass
