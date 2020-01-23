from flask_sqlalchemy import SQLAlchemy
from skeletor.utility.decorators import singleton


@singleton
class PostGressConnection(object):
    __db__: SQLAlchemy = None

    def __init__(self, *args, **kwargs):
        if 'app' in kwargs:
            self.__db__ = SQLAlchemy(kwargs['app'])

    def get(self) -> SQLAlchemy:
        return self.__db__
