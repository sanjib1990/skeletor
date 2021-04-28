from datetime import datetime

from flask import session

from skeletor.config import DATE_TIME_FORMAT
from skeletor.utility.decorators import is_logged_in
from src.repositories.postgress.user import User as UserRepo
from src.resources.base import BaseController


class SignOut(BaseController):
    def __init__(self, *args, **kwargs):
        super(SignOut, self).__init__(*args, **kwargs)
        self.user = UserRepo()
        pass

    def get_search_dict(self):
        return {}

    @is_logged_in
    def get(self):
        user = session.get('user', {})
        if user:
            self.logger.info("user logged out {0}".format(user))
            update_dict = {
                "updated_by": user.get('email'),
                "is_online": False,
                "is_loggedin": False,
                "last_login": datetime.utcnow().strftime(DATE_TIME_FORMAT),
                "email": user.get('email')
            }
            result = self.user.update_user(**update_dict)
            user = session.pop('user', {})
            if "errors" in result:
                return self.renderer.render(result, 400)
            return self.renderer.render({"message": "Signed out %s" % (user["email"])})
