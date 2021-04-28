from skeletor import JSONRenderer
from skeletor.utility.decorators import is_logged_in
from src.repositories.graph.product import ProductRepo
from src.resources.base import BaseController


class ProductController(BaseController):
    def __init__(self, *args, **kwargs):
        super(ProductController, self).__init__(*args, **kwargs)
        self.renderer = JSONRenderer()
        self.repo = ProductRepo()
        pass

    def get_search_dict(self):
        return {}

    @is_logged_in
    def get(self, product_id=None):
        self.logger.info(f"LOGGING FOR ID {product_id}")
        return self.renderer.render(self.repo.get_by_id(product_id))

