import copy
import bson
from skeletor import db
from skeletor.config import DATE_TIME_FORMAT
from skeletor.utility.exceptions.general_error import GeneralException
from skeletor.utility.logger import Logger
from sqlalchemy.dialects.postgresql import JSONB
from skeletor.utility.caching.cachable import Cachable


class BaseModel(db.Model, Cachable):
    __abstract__ = True
    es_name = None
    __table_args__ = {'extend_existing': True}

    _id = db.Column(db.Integer, primary_key=True)
    object_id = db.Column(db.String(32), unique=True, nullable=False)
    data = db.Column(JSONB)
    is_active = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime,
        onupdate=db.func.now(),
        server_default=db.func.now()
    )
    created_by = db.Column(db.String(50), nullable=True)
    updated_by = db.Column(db.String(50), nullable=True)
    logger = None

    def __init__(self, *args, **kwargs):
        self.data = kwargs.get('data') if 'data' in kwargs else None
        self.object_id = str(bson.ObjectId())
        self.logger = Logger().get(self.__class__.__name__)
        pass

    @property
    def cache_key(self):
        return 'object_id'

    def get_base_dict(self) -> dict:
        return {
            "_id": self._id,
            "object_id": self.object_id,
            "data": self.data,
            "is_active": self.is_active,
            "created_at": self.created_at.strftime(DATE_TIME_FORMAT) if self.created_at is not None else None,
            "updated_at": self.updated_at.strftime(DATE_TIME_FORMAT) if self.updated_at is not None else None,
            "created_by": self.created_by,
            "updated_by": self.updated_by
        }

    def _update_data(self, **kwargs):
        data = copy.deepcopy(self.data) or {}
        data.update(kwargs)
        self.data = data

    def asdict(self, *args, **kwargs) -> dict:
        return {c.key: getattr(self, c.key)
                for c in db.inspect(self).mapper.column_attrs}

    def exists(self, kwargs=None) -> bool:
        """
        Check existance of a row.
        :param self: the Model class name
        :param kwargs: filter params
        :return: bool
        """
        if not kwargs:
            data = self.asdict()

            # filter out object id and None data
            params = {}
            for x, y in data.items():
                if x != 'object_id' and y is not None:
                    params[x] = y
                    pass
                pass

            if not params:
                raise GeneralException(message='No value provided for search')
            return self.exists(params)

        data = self.query.filter_by(**kwargs).first()

        return True if data else False

    def convert_includes_dict(self, includes) -> dict:
        """
        :param includes: includes could be comma separated string or a list of string.
        :return: dict
        """
        obj = {}
        if includes is None:
            return obj

        if isinstance(includes, str):
            includes = [x.strip() for x in includes.split(',')]

        for _, v in enumerate(includes):
            dotlist = [x.strip() for x in v.split('.')]
            zeroitem = dotlist[0]
            dotlist.pop(0)
            obj[zeroitem] = ''
            if dotlist:
                obj[zeroitem] = '.'.join(str(e) for e in dotlist)

        return obj

    def handle_includes(self, **kwargs):
        includes = kwargs.get('includes')
        if isinstance(includes, str):
            includes = [x.strip() for x in includes.split(',')]

        return self.convert_includes_dict(includes)

    def get_es_index_mapping(self):
        from src.repositories.elasticsearch.elastic_base import ElasticInsertRepo
        search = ElasticInsertRepo()
        return {
            self.es_name: {
                'properties': {
                    "id": search.id_mapping,
                    "name": search.text_mapping,
                    "alias": search.text_mapping,
                    "is_active": search.boolean_mapping,
                    "created_by": search.email_mapping,
                    "updated_by": search.email_mapping,
                    "created_at": search.date_mapping,
                    "updated_at": search.date_mapping
                }
            }
        }
