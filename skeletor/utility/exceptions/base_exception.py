
class AbstractException(Exception):
    error_dict = {}
    report = True

    def __init__(self, *args, **kwargs):
        for k, v in kwargs.items():
            self.error_dict[k] = v
            pass

        if 'report' in kwargs:
            self.report = kwargs.get('report')

        """TO DO: Handle args as well"""
