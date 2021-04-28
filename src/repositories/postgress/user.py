from datetime import datetime
from typing import List
from werkzeug.security import check_password_hash, generate_password_hash

from skeletor import db
from skeletor.config import DATE_TIME_FORMAT
from skeletor.utility.exceptions.general_error import GeneralException
from skeletor.utility.jwt_auth import JWTAuth
from src.models.postgress.user import User as UserModel
from src.repositories.arango.base import Base


class User(Base):
    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)

    @property
    def schema(self):
        return {
            "type": "object",
            "properties": {
                "email": {
                    "type": "string",
                    "format": "email"
                },
                "password": {
                    "type": "string",
                    "maxLength": 150,
                    "minLength": 6
                },
                "is_online": {
                    "type": "boolean"
                },
                "last_login": {
                    "type": "string",
                    "format": "date-time"
                },
                "_id": {
                    "type": "number",
                },
                "object_id": {
                    "type": "string",
                    "maxLength": 64
                },
                "updated_by": {
                    "type": "string",
                    "format": "email"
                },
                "is_active": {
                    "type": "boolean"
                },
                "data": {
                    "type": "object"
                }
            }
        }

    @staticmethod
    def token(email):
        user = UserModel.query.filter_by(email=email).first()
        return JWTAuth().token({'id': user.object_id})

    def check_password(self, password_hash, password):
        return check_password_hash(password_hash, password)

    def change_user_state(self, object_id, is_online=False):
        user = self.find(**{'object_id': object_id, 'is_active': True})
        if not user:
            raise GeneralException(message='User not found.')

        # update the user state
        user.is_online = is_online
        db.session.commit()

        pass

    def create_user(self, data):
        error = self.validate_data(data)
        if error:
            return error
        try:
            user = UserModel()
            user.email = data.get('email')
            user.is_active = True
            user.password = generate_password_hash(
                data.get("password", "iambatman"))
            user.updated_by = data.get('updated_by')
            user.created_by = data.get('created_by')
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            self.logger.fatal('User insert error: {0}'.format(e))
            return {
                "errors": "db error: Something went wrong while inserting user"}
        return user.asdict()

    def fetch(self, **kwargs):
        return UserModel.query.filter_by(**kwargs).all()

    def fetch_items(self, **kwargs):
        param: List[tuple] = []

        if 'object_ids' in kwargs:
            param.append(
                UserModel.object_id.in_(
                    tuple(
                        kwargs.get('object_ids'))))

        if 'is_active' in kwargs:
            param.append(UserModel.is_active.__eq__(kwargs.get('is_active')))

        if 'is_online' in kwargs:
            param.append(UserModel.is_online.__eq__(kwargs.get('is_online')))

        if 'object_id' in kwargs:
            param.append(UserModel.object_id.__eq__(kwargs.get('object_id')))

        if 'is_loggedin' in kwargs:
            param.append(UserModel.is_loggedin.__eq__(kwargs.get('is_loggedin')))

        return UserModel.query.filter(*tuple(param)).all()

    def find(self, **kwargs):
        return UserModel.query.filter_by(**kwargs).first()

    def authenticate(self, email, password):
        user = self.find(email=email, is_active=True)
        if user is not None and not isinstance(
                user, list) and self.check_password(
                user.password, password):
            return user.asdict()
        return None

    def update_user(self, **kwargs):
        self.logger.info("update_user {0}".format(kwargs))
        error = self.validate_data(kwargs)
        if error:
            return error
        user = None
        if not {"object_id", "_id", "email"}.intersection(set(kwargs.keys())):
            return {"errors": '"object_id" and "_id" and "email" not present'}
        elif kwargs.get('object_id', None):
            user = UserModel.query.filter_by(
                object_id=kwargs.pop('object_id')).first()
        elif kwargs.get('_id', None):
            user = UserModel.query.filter_by(_id=kwargs.pop('_id')).first()
        else:
            user = UserModel.query.filter_by(email=kwargs.pop('email')).first()
        try:
            if 'password' in kwargs:
                user.password = generate_password_hash(kwargs.get('password'))
            if 'data' in kwargs:
                user._update_date(**kwargs.get('data'))
            if 'last_login' in kwargs:
                user.last_login = datetime.strptime(
                    kwargs.get('last_login'), DATE_TIME_FORMAT)
            if 'is_active' in kwargs:
                user.is_active = kwargs.get('is_active')
            if 'is_online' in kwargs:
                user.is_online = kwargs.get('is_online')
            if 'is_loggedin' in kwargs:
                user.is_loggedin = kwargs.get('is_loggedin')
            if 'updated_by' in kwargs:
                user.updated_by = kwargs.get('updated_by')

            self.logger.info("user updated {0}".format(user.asdict()))

            db.session.commit()
        except Exception as e:
            self.logger.fatal('User insert error: {0}'.format(e))
            return {
                "errors": "db error: Something went wrong while updating user"}
        return user.asdict()
