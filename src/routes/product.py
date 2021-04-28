from flask import Blueprint
from flask_restful import Api

from src.resources.elastic.product import ElasticProductController
from src.resources.graph.product import ProductController


blueprint = Blueprint('product', __name__, url_prefix=r'/api')
api = Api()
api.init_app(blueprint)

api.add_resource(ElasticProductController, r"/elastic/products/<string:product_id>",)
api.add_resource(ProductController, r"/products/<string:product_id>",)
