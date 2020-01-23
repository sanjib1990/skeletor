from .base_exception import AbstractException


class ValidationException(AbstractException):
    def __init__(self, *args, code=400, message="Validation failed", **kwargs):
        kwargs['code'] = code
        kwargs['message'] = message
        super(ValidationException, self).__init__(*args, **kwargs)
