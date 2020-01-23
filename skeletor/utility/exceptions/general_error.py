from .base_exception import AbstractException


class GeneralException(AbstractException):
    def __init__(self, *args, **kwargs):
        super(GeneralException, self).__init__(*args, **kwargs)
