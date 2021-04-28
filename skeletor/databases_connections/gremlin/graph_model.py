from skeletor import graph
from gremlin_python.process.graph_traversal import GraphTraversalSource

from src.models.graph.entities.base_entity import BaseEntity


class GraphModel(object):
    g: GraphTraversalSource = None
    entity: BaseEntity = None

    def __init__(self, *args, **kwargs):
        self.g = graph.get_traversal()
        pass
