from .base_exception import AbstractException


class AlreadyExistsException(AbstractException):
    def __init__(self, *args, code=400, message="Entity already exists", **kwargs):
        kwargs['code'] = code
        kwargs['message'] = message
        super(AlreadyExistsException, self).__init__(*args, **kwargs)
