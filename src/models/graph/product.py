from skeletor.databases_connections.gremlin.graph_model import GraphModel
from gremlin_python.process.traversal import T
from src.models.graph.entities.product_entity import ProductEntity


class Product(GraphModel):
    def __init__(self, *args, **kwargs):
        super(Product, self).__init__(*args, **kwargs)
        self.entity = ProductEntity()
        pass

    def transform(self, entity):
        data = {
            'id': entity.get(T.id)
        }
        return {**data, **{k: v[0] for k, v in entity.items() if k not in [T.id, T.label]}}
