from datetime import datetime
from typing import List
from werkzeug.security import check_password_hash, generate_password_hash

from skeletor import db
from skeletor.config import DATE_TIME_FORMAT
from skeletor.utility.exceptions.general_error import GeneralException
from skeletor.utility.jwt_auth import JWTAuth
from src.models.postgress.feature_flag import FeatureFlag
from src.models.postgress.user import User as UserModel
from src.repositories.arango.base import Base


class FeatureFlagRepo(Base):
    def __init__(self, *args, **kwargs):
        super(FeatureFlagRepo, self).__init__(*args, **kwargs)

    @property
    def schema(self):
        return {}

    def create(self, data):
        try:
            model = FeatureFlag()
            model.name = data.get('name')
            model.value = data.get('value')
            model.is_active = True
            model.updated_by = data.get('updated_by')
            model.created_by = data.get('created_by')
            db.session.add(model)
            db.session.commit()
        except Exception as e:
            self.logger.fatal('FeatureFlag insert error: {0}'.format(e))
            return {
                "errors": "db error: Something went wrong while inserting user"}
        return model.asdict()

    def fetch(self, **kwargs):
        return FeatureFlag.query.filter_by(**kwargs).all()

    def find(self, **kwargs):
        return FeatureFlag.query.filter_by(**kwargs).first()

    def update(self, **kwargs):
        self.logger.info("update {0}".format(kwargs))
        model = FeatureFlag.query.filter_by(name=kwargs.pop('name')).first()
        try:
            if 'value' in kwargs:
                model.value = kwargs.get('value')

            self.logger.info("user updated {0}".format(model.asdict()))

            db.session.commit()
        except Exception as e:
            self.logger.fatal('FeatureFlag insert error: {0}'.format(e))
            return {
                "errors": "db error: Something went wrong while updating user"}
        return model.asdict()
