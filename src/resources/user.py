import copy
from datetime import datetime
from flask import request, session
from flask_restful import Resource
from skeletor.utility.logger import Logger
from skeletor.config import DATE_TIME_FORMAT
from skeletor.utility.decorators import login_required, authenticate
from skeletor.utility.renderers import JSONRenderer
from src.models import User
from src.repositories.user import User as UserRepo


class SignUp(Resource):
    def __init__(self, *args, **kwargs):
        super(SignUp, self).__init__(*args, **kwargs)
        self.renderer = JSONRenderer()
        self.user = UserRepo()
        self.logger = Logger().get(self.__class__.__name__)

    @login_required
    @authenticate
    def post(self):
        self.logger.info("LOGGING")
        data = copy.deepcopy(request.json)
        error = self.user.validate_data(data)
        if error:
            return self.renderer.render({"errors": error}, 400)
        current_user = session.get('user')['email']
        if self.user.fetch(email=data.get('email')):
            return self.renderer.render(
                {"errors": "User with this email already exists"}, 400)
        data.update({
            "updated_by": current_user,
            "created_by": current_user
        })
        result = self.user.create_user(data)
        if "errors" in result:
            return self.renderer.render(result, 400)
        return self.renderer.render(result, exclude=['password'])


class SignIn(Resource):
    def __init__(self, *args, **kwargs):
        super(SignIn, self).__init__(*args, **kwargs)
        self.renderer = JSONRenderer()
        self.user = UserRepo()
        self.logger = Logger().get(self.__class__.__name__)

    def post(self):
        self.logger.info("LOGGING")

        data = copy.deepcopy(request.json)
        self.logger.info("user logged in {0}".format(data))

        error = self.user.validate_data(data)
        self.logger.info("SignIn error {0}".format(error))

        if error:
            return self.renderer.render({"errors": error}, 400)

        user = self.user.authenticate(
            data.get('email'),
            data.get('password')
        )
        if not user:
            return self.renderer.render({"errors": "User doesn't exist or deactivated"}, 400)

        if user.get('is_loggedin'):
            return self.renderer.render({
                "errors": "Already loggedin"
            }, 400)

        update_dict = {
            "_id": user.get('_id'),
            "is_online": True,
            "is_loggedin": True,
            "last_login": datetime.utcnow().strftime(DATE_TIME_FORMAT),
            "updated_by": user.get('email')
        }

        if 'social_auth' in data and data['social_auth']:
            update_dict.update({'data': {'social_auth': data['social_auth']}})

        result = self.user.update_user(**update_dict)
        if "errors" in result:
            return self.renderer.render(result, 400)
        _user: User = self.user.find(object_id=user.get('object_id'))
        result = {
            "email": user.get('email'),
            "object_id": user.get('object_id')
        }
        return self.renderer.render(result)
