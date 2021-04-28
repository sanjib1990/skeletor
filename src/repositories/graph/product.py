from src.models.graph.product import Product


class ProductRepo(object):
    model = Product()

    def __init__(self, *args, **kwargs):
        pass

    def get_by_id(self, _id):
        _data = self.model.g.V(_id).hasLabel(self.model.entity.LABEL).valueMap(True).toList()
        return self.model.transform(_data.pop()) if _data else {}

    def get_all(self):
        _data = self.model.g.V().hasLabel(self.model.entity.LABEL).valueMap(True).toList()
        return [self.model.transform(x) for x in _data]
