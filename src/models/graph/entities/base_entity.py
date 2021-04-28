import inspect


class BaseEntity(object):
    ID = 'id'
    LABEL = None
    ALIAS = None
    NAME = 'name'
    EDGES_FROM = {}
    EDGES_TO = {}
    CREATED_AT = 'created_at'
    UPDATED_AT = 'updated_at'
    CREATED_BY = 'created_by'
    UPDATED_BY = 'updated_by'
    IS_ACTIVE = 'is_active'

    @classmethod
    def dict(cls):
        data = {}
        for a, b in inspect.getmembers(cls, lambda a: not (inspect.isroutine(a))):
            if str(a).startswith('_') or str(a).endswith('_'):
                continue
            data.update({a: b})
        return data
