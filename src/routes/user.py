from flask import Blueprint
from flask_restful import Api
from src.resources.postgress.sign_in import SignIn
from src.resources.postgress.sign_up import SignUp
from src.resources.postgress.sign_out import SignOut

blueprint = Blueprint('user', __name__, url_prefix=r'/api/user')
api = Api()
api.init_app(blueprint)

api.add_resource(SignIn, r"/signin")
api.add_resource(SignUp, r"/signup")
api.add_resource(SignOut, r"/signout")
