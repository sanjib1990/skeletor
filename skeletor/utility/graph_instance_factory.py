from skeletor import Logger
from skeletor.databases_connections.gremlin.graph_model import GraphModel


class GraphInstanceFactory(GraphModel):
    t = None
    logger = Logger().get(__name__)

    def __init__(self):
        super().__init__()
