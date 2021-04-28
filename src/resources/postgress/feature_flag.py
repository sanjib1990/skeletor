import copy
from datetime import datetime

from flask import session
from redis import Redis

from skeletor.config import CACHES, DATE_TIME_FORMAT
from src.repositories.postgress.feature_flag import FeatureFlagRepo
from src.repositories.postgress.identity import IdentityRepo
from src.resources.base import BaseController
from src.repositories.postgress.user import User as UserRepo
from src.models.postgress.user import User
from src.services.user_context import UserContext


class FeatureFlagController(BaseController):
    def __init__(self, *args, **kwargs):
        super(FeatureFlagController, self).__init__(*args, **kwargs)
        self._repo = FeatureFlagRepo()
        self.identity = IdentityRepo()
        pass

    def get_search_dict(self):
        return {}

    def post(self):
        self.logger.info("LOGGING")
        data = copy.deepcopy(self.get_body())
        item = self._repo.create(data)
        self.logger.info(f"{item}")
        return self.renderer.render(item)

    def put(self, object_id=None):
        self.logger.info("LOGGING")
        data = copy.deepcopy(self.get_body())
        item = self._repo.update(**data)
        self.logger.info(f"{item}")
        return self.renderer.render(item)

    def get(self, user_identity, flag_name):
        """
        identy and feature flag prioritize the identity
        """
        _feature_flag = self._repo.find(name=flag_name)
        _identity = self.identity.find(identity=user_identity, feature_flag_id=_feature_flag._id)
        res = {
        }
        if _identity:
            res[flag_name] = _identity.value
        else:
            res[flag_name] = _feature_flag.value
        return self.renderer.render(res)
