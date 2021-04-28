from src.repositories.elasticsearch.elastic_base import ElasticSearchRepo


class Product(object):
    __index__ = 'graph_product_index'
    __type__ = 'product'

    def __init__(self, *args, **kwargs):
        self.base = ElasticSearchRepo()

    def get_by_id(self, product_id):
        return self.base.get_by_id(self.__index__, self.__type__, product_id)
