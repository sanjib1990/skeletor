from flask import Blueprint
from flask_restful import Api
from src.resources.product import ElasticProductController, ProductController


blueprint = Blueprint('product', __name__, url_prefix=r'/api')
api = Api()
api.init_app(blueprint)

api.add_resource(ElasticProductController, r"/elastic/get_product/<string:product_id>",)
api.add_resource(ProductController, r"/get_product/<string:product_id>",)
