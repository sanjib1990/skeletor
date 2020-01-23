import base64
import functools
import time
from functools import wraps
from datetime import datetime
from flask import session, request
from .exceptions.general_error import GeneralException
from .renderers import JSONRenderer
from .jwt_auth import JWTAuth
from ..config import DATE_TIME_FORMAT

renderer = JSONRenderer()


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if session.get('user'):
            return func(*args, **kwargs)
        else:
            return renderer.render({"errors": "Login required"}, 401)
    return wrapper


def do_db_auth(*args, **kwargs):
    if 'Authorization' not in request.headers or 'Token' not in str(
            request.headers['Authorization']):
        return False, "Invalid Authorization", 403
    else:
        auth = JWTAuth()
        auth_header = request.headers['Authorization'].split()
        prefix = auth_header[0]
        token = auth_header[1] if len(auth_header) > 1 else ""
        if prefix != 'Token':
            return False, "Invalid Authorization", 403
        user = auth.authenticate_token(bytes(token, 'utf-8'))
        _user = session.get('user')
        errors = []
        if 'errors' not in user and _user:
            token_user_id = user.get('id')
            session_user_id = _user.get('object_id')
            if token_user_id == session_user_id:
                return True, "", 200
            else:
                errors.append("Invalid Token")
        else:
            if isinstance(user.get('errors'), list):
                errors += user.get('errors')
            else:
                errors.append(user.get('errors'))

        if errors:
            if _user:
                from src.repositories.user import User as UserRepo
                user_repo = UserRepo()
                result = user_repo.update_user(**{
                    "updated_by": _user.get('email'),
                    "is_online": False,
                    "is_loggedin": False,
                    "last_login": datetime.utcnow().strftime(DATE_TIME_FORMAT),
                    "email": _user.get('email')
                })
                session.pop('user', {})
                if "errors" in result:
                    if isinstance(result.get('errors'), list):
                        errors += result.get('errors')
                    else:
                        errors.append(result.get('errors'))
            return False, errors, 401
    pass


def authenticate(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        proceed, message, code = do_db_auth(*args, **kwargs)
        if not proceed:
            return renderer.render({"errors": message}, code)
        return func(*args, **kwargs)
    return wrapper


def decode_token(auth_header):
    bearer = auth_header[0].lower()
    encoded_str = auth_header[1] if len(auth_header) > 1 else ""
    decoded_str = base64.b64decode(encoded_str).decode()
    if ':' not in decoded_str:
        raise GeneralException(message="Token provided is not valid", status=403)
    encoded_token, timestamp = decoded_str.split(':')
    current_time = int(time.time() * 1000)
    diff = current_time - int(timestamp)
    if not timestamp.isdigit() or diff > 20000:
        raise GeneralException(message="Token provided is not valid", status=403)
    key = base64.b64encode((bearer+str(timestamp)).encode()).decode()
    token, validate_key = base64.b64decode(encoded_token.encode()).decode().split('.')
    if key != validate_key:
        raise GeneralException(message="Token provided is not valid", status=403)
    return token, bearer


def do_ext_auth(*args, **kwargs):
    try:
        app_key_ext_auth = 'ext_auth_keys'
        if 'Authorization' not in request.headers:
            return False, "Invalid Authorization", 403
        else:
            auth_header = request.headers['Authorization'].split()
            token, bearer = decode_token(auth_header)
            from src.repositories.app_property import AppPropertyRepo
            app_props = AppPropertyRepo().get()
            if not app_props \
                    or app_key_ext_auth not in app_props \
                    or bearer not in app_props[app_key_ext_auth] \
                    or token != app_props[app_key_ext_auth][bearer]:
                return False, "Cannot be authenticated", 403
            pass
        return True, None, None
    except Exception as e:
        return False, "Cannot be authenticated", 403


def auth_ext_triggers(func):
    """
    Expected authorization token:
    -> time: 13 digit time stamp
    -> name: Name of application registerd
    -> token: Token givem
    -> Authorization: name base64encode<bas64encode<token + '.' + bas64encode<name+time>>+ ':' + time>
    :param func:
    :return:
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        proceed, message, code = do_ext_auth(*args, **kwargs)
        if not proceed:
            return renderer.render({"errors": message}, code)
        return func(*args, **kwargs)
    return wrapper


def is_logged_in(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        proceed = True
        message = ""
        code = 200
        if not session.get('user'):
            proceed = False
            message = "Login required"
            code = 401

        if session.get('user'):
            proceed, message, code = do_db_auth(*args, **kwargs)

        proceed_, message_, code_ = do_ext_auth(*args, **kwargs)
        proceed = proceed or proceed_
        if not proceed_:
            message = message_
            code = code_

        if not proceed:
            return renderer.render({"errors": message}, code)

        return func(*args, **kwargs)
    return wrapper


def remove_includes(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'includes' in kwargs:
            del kwargs['includes']
        return func(*args, **kwargs)
    return wrapper


def singleton(cls):
    """Make a class a Singleton class (only one instance)"""
    @functools.wraps(cls)
    def wrapper_singleton(*args, **kwargs):
        if not wrapper_singleton.instance:
            wrapper_singleton.instance = cls(*args, **kwargs)
        return wrapper_singleton.instance
    wrapper_singleton.instance = None
    return wrapper_singleton
