from flask_restful import Resource

from skeletor import JSONRenderer
from skeletor.utility.logger import Logger
from src.repositories.elasticsearch.product import Product as ElasticProduct
from src.repositories.graph.product import ProductRepo


class ProductController(Resource):
    def __init__(self, *args, **kwargs):
        super(ProductController, self).__init__(*args, **kwargs)
        self.renderer = JSONRenderer()
        self.repo = ProductRepo()
        self.logger = Logger().get(self.__class__.__name__)

    def get(self, product_id=None):
        self.logger.info(f"LOGGING FOR ID {product_id}")
        return self.renderer.render(self.repo.get_by_id(product_id))


class ElasticProductController(Resource):
    def __init__(self, *args, **kwargs):
        super(ElasticProductController, self).__init__(*args, **kwargs)
        self.renderer = JSONRenderer()
        self.repo = ElasticProduct()
        self.logger = Logger().get(self.__class__.__name__)

    def get(self, product_id=None):
        self.logger.info(f"LOGGING FOR ID {product_id}")
        return self.renderer.render(self.repo.get_by_id(product_id))

