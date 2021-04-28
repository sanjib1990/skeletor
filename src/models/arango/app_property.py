from skeletor.databases_connections.arango.arango_model import BaseDoc


class AppProperty(BaseDoc):
    """
    No migration needs to be created for this model. It's modeled for Arango.
    """
    __collection_name__ = "app_properties"

    def __init__(self, *args, **kwargs):
        super(AppProperty, self).__init__(*args, **kwargs)

    def asdict(self, *args, **kwargs) -> dict:
        return {
            "_id": self._id,
            "_key": self._key,
            "data": self.data,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "created_by": self.created_by,
            "updated_by": self.updated_by
        }

    def result(self, data) -> dict:
        return data.get('data')

    def __repr__(self):
        return "<AppProperty(_id='%s')>" % self._key

    @property
    def cache_key(self):
        return '_key'
