from .base_exception import AbstractException


class NotFoundException(AbstractException):
    def __init__(self, *args, code=404, message="Entity Not Found", **kwargs):
        kwargs['code'] = code
        kwargs['message'] = message
        super(NotFoundException, self).__init__(*args, **kwargs)
