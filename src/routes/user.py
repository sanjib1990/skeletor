from flask import Blueprint
from flask_restful import Api

from src.resources.user import SignIn, SignUp


blueprint = Blueprint('user', __name__, url_prefix=r'/api/user')
api = Api()
api.init_app(blueprint)

api.add_resource(SignIn, r"/signin")
api.add_resource(SignUp, r"/signup")
