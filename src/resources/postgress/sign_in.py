import copy
from datetime import datetime

from flask import session
from redis import Redis

from skeletor.config import CACHES, DATE_TIME_FORMAT
from src.resources.base import BaseController
from src.repositories.postgress.user import User as UserRepo
from src.models.postgress.user import User
from src.services.user_context import UserContext


class SignIn(BaseController):
    def __init__(self, *args, **kwargs):
        super(SignIn, self).__init__(*args, **kwargs)
        self.repo = UserRepo()
        self._redis = Redis(host=CACHES['HOST'], port=CACHES['PORT'], db=1)
        pass

    def get_search_dict(self):
        return {}

    def __remove_prev_activity__(self, object_id=None):
        sid = self._redis.get(object_id)
        if isinstance(sid, bytes):
            self.logger.info(f"Removed sessions {self._redis.delete(b'skeletor_session:'+sid)}-{self._redis.delete(object_id)}")
        return sid

    def post(self):
        self.logger.info("LOGGING")
        data = copy.deepcopy(self.get_body())
        self.logger.info(f"user logged in {data}")

        error = self.repo.validate_data(data)
        self.logger.info(f"SignIn error {error}")

        if error:
            return self.renderer.render({"errors": error}, 400)

        user = self.repo.authenticate(
            data.get('email'),
            data.get('password')
        )
        if not user:
            return self.renderer.render({"errors": "User doesn't exist or deactivated"}, 400)

        if user.get('is_loggedin') and not data.get("deactivate_previous_session", None):
            return self.renderer.render({
                "deactivate_previous_session": None,
                "errors": "Active session found!!, Do you want to logout from other device(s)?"
            }, 400)

        if data.get("deactivate_previous_session", None):
            sid = self.__remove_prev_activity__(user.get('object_id', None))
            self.logger.info(f"Active session of email {data.get('email', None)} {sid}")

        update_dict = {
            "_id": user.get('_id'),
            "is_online": True,
            "is_loggedin": True,
            "last_login": datetime.utcnow().strftime(DATE_TIME_FORMAT),
            "updated_by": user.get('email')
        }

        if 'social_auth' in data and data['social_auth']:
            update_dict.update({'data': {'social_auth': data['social_auth']}})

        result = self.repo.update_user(**update_dict)
        if "errors" in result:
            return self.renderer.render(result, 400)
        _user: User = self.repo.find(object_id=user.get('object_id'))
        result = {
            "email": user.get('email'),
            "object_id": user.get('object_id')
        }

        if session.get('user'):
            session.pop('user')
        session['user'] = result
        self._redis.setex(user.get('object_id'), 86400, session.sid)

        result.update({'token': self.repo.token(user['email'])})
        UserContext().set_user_obj(object_id=user.get('object_id'))
        return self.renderer.render(result)
