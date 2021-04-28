import copy
from flask import session
from src.repositories.postgress.user import User as UserRepo
from src.resources.base import BaseController


class SignUp(BaseController):
    def __init__(self, *args, **kwargs):
        super(SignUp, self).__init__(*args, **kwargs)
        self.repo = UserRepo()
        pass

    def get_search_dict(self):
        return {}

    def post(self):
        self.logger.info("LOGGING")
        data = copy.deepcopy(self.get_body())
        error = self.repo.validate_data(data)
        if error:
            return self.renderer.render({"errors": error}, 400)
        current_user = session.get('user')['email']
        if self.repo.fetch(email=data.get('email')):
            return self.renderer.render(
                {"errors": "User with this email already exists"}, 400)
        data.update({
            "updated_by": current_user,
            "created_by": current_user
        })
        result = self.repo.create_user(data)
        if "errors" in result:
            return self.renderer.render(result, 400)
        return self.renderer.render(result, exclude=['password'])
