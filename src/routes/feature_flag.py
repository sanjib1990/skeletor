from flask import Blueprint
from flask_restful import Api

from src.resources.postgress.feature_flag import FeatureFlagController
from src.resources.postgress.sign_in import SignIn
from src.resources.postgress.sign_up import SignUp
from src.resources.postgress.sign_out import SignOut

blueprint = Blueprint('interview', __name__, url_prefix=r'/api/features')
api = Api()
api.init_app(blueprint)

api.add_resource(FeatureFlagController, r"", r"/<string:user_identity>/<string:flag_name>")
