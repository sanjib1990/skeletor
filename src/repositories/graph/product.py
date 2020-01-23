from src.models.graph.product import Product


class ProductRepo(object):
    model = Product()

    def __init__(self, *args, **kwargs):
        pass

    def get_by_id(self, _id):
        _data = self.model.g.V(_id).valueMap(True).toList()
        return self.model.transform(_data[0])
