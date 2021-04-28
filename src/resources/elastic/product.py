from src.repositories.elasticsearch.product import Product as ElasticProduct
from src.resources.base import BaseController


class ElasticProductController(BaseController):
    def __init__(self, *args, **kwargs):
        super(ElasticProductController, self).__init__(*args, **kwargs)
        self.repo = ElasticProduct()
        pass

    def get_search_dict(self):
        return {}

    def get(self, product_id=None):
        self.logger.info(f"LOGGING FOR ID {product_id}")
        return self.renderer.render(self.repo.get_by_id(product_id))
