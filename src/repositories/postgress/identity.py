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
from src.models.postgress.identity import Identity


class IdentityRepo(Base):
    def __init__(self, *args, **kwargs):
        super(IdentityRepo, self).__init__(*args, **kwargs)

    @property
    def schema(self):
        return {}

    def create(self, data):
        try:
            model = Identity()
            model.identity = data.get('identity')
            model.feature_flag_id = data.get('feature_flag_id')
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
        return Identity.query.filter_by(**kwargs).all()

    def find(self, **kwargs):
        return Identity.query.filter_by(**kwargs).first()

    def update(self, **kwargs):
        self.logger.info("update {0}".format(kwargs))
        if not {"object_id", "_id", "email"}.intersection(set(kwargs.keys())):
            return {"errors": '"object_id" and "_id" and "email" not present'}
        elif kwargs.get('object_id', None):
            model = Identity.query.filter_by(object_id=kwargs.pop('object_id')).first()
        elif kwargs.get('_id', None):
            model = Identity.query.filter_by(_id=kwargs.pop('_id')).first()
        else:
            model = Identity.query.filter_by(name=kwargs.pop('name')).first()
        try:
            if 'value' in kwargs:
                model.vlue = kwargs.get('value')

            self.logger.info("user updated {0}".format(model.asdict()))

            db.session.commit()
        except Exception as e:
            self.logger.fatal('FeatureFlag insert error: {0}'.format(e))
            return {
                "errors": "db error: Something went wrong while updating user"}
        return model.asdict()
