import jwt
from datetime import datetime, timedelta

from flask import current_app

class JWTAuth(object):
    def _generate_jwt_token(self, extra_details):
        dt = datetime.now()
        data = {
            'nbf': int(dt.strftime('%s')),
            'iat': int(dt.strftime('%s')),
            'exp': int((dt + timedelta(days=1)).strftime('%s'))
            # 'exp': int((dt + timedelta(minutes=1)).strftime('%s'))
        }
        data.update(extra_details)
        return jwt.encode(
            data,
            current_app.config["SECRET_KEY"],
            algorithm='HS256'
        ).decode('utf-8')
    
    def token(self, extra_details={}):
        return self._generate_jwt_token(extra_details)

    def authenticate_token(self, token):
        """
        Try to authenticate the given credentials. If authentication is
        successful, return the user and token. If not, throw an error.
        """
        try:
            return jwt.decode(
                token, current_app.config["SECRET_KEY"], algorithm='HS256')
        except jwt.exceptions.InvalidSignatureError:
            return {'errors': ['Signature verification failed.']}
        except:
            return {'errors': ['Invalid authentication. Could not decode token.']}
