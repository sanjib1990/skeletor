from flask import session
from flask_restful import abort
from skeletor.utility.caching.base_cache import Caching
from src.models import User
from src.repositories.user import User as UserRepo


class UserContext:
    def __init__(self):
        self.cache = Caching().db

    def set_user_obj(self, object_id: str):
        user_repo = UserRepo()
        user = user_repo.find(
            object_id=object_id
        )
        session['user_ctx'] = user
        # self.cache.set(session.sid + ':user', user)

    def user(self) -> User:
        user = session['user_ctx']
        if user is None:
            abort(401)

        return user
