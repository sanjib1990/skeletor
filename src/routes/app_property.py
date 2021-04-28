from flask import Blueprint
from flask_restful import Api
from src.resources.arango.app_property import AppPropertyController

blueprint = Blueprint('app_properties', __name__, url_prefix=r'/api/properties')
api = Api()
api.init_app(blueprint)

api.add_resource(AppPropertyController, r"", r"/")
