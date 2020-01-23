import abc
import copy

import bson

from skeletor import doc
from datetime import datetime
from arango import ArangoClient
from arango.database import TransactionDatabase
from skeletor.config import DATE_TIME_FORMAT
from skeletor.utility.caching.cachable import Cachable
from skeletor.utility.logger import Logger


class BaseDoc(Cachable):
    __table_args__ = {"sync": True, "user_keys": True}
    __db__: TransactionDatabase = None

    _id = None
    data = None
    is_active = None
    created_at = None
    updated_at = None
    created_by = None
    updated_by = None
    __collection_name__ = None

    aql_query = None
    sort_clause = ''
    limit_clause = ''
    filter_clause = ''
    filter_dict = {}
    _key = None
    __before_filter__ = ""
    __raw_filter__ = ""
    logger = None

    def get_client(self) -> ArangoClient:
        return doc.client

    def __init__(self, *args, **kwargs):
        self._key = kwargs.get('object_id') if 'object_id' in kwargs else kwargs.get('_key', str(bson.ObjectId()))
        self.data = kwargs.get('data') if 'data' in kwargs else None
        self._id = kwargs.get('_id', None)
        self.object_id = kwargs.get('object_id', None)
        self.is_active = kwargs.get('is_active', None)
        self.created_at = kwargs.get('created_at', self.date_time_now())
        self.updated_at = kwargs.get('updated_at', self.date_time_now())
        self.created_by = kwargs.get('created_by', None)
        self.updated_by = kwargs.get('updated_by', None)
        self.logger = Logger().get(self.__class__.__name__)

        if '__db__' in kwargs:
            self.__db__ = kwargs.get('__db__')

    def date_time_now(self):
        return datetime.utcnow().strftime(DATE_TIME_FORMAT)

    @property
    def db(self):
        if self.__db__:
            return self.__db__.collection(self.__collection_name__)

        return doc.db.collection(self.__collection_name__)

    @property
    def aql(self):
        return doc.db.aql

    def set_aql_query(self):
        self.aql_query = "FOR doc in " + self.__collection_name__
        return self

    def sort(self, name, order):
        self.sort_clause = ' sort doc.' + name + ' ' + order
        pass

    def limit(self, *args):
        self.limit_clause = f' limit {args[0]} '
        if len(args) == 2:
            self.limit_clause += f', {args[1]} '

    def before_filter(self, before_filter: str):
        self.__before_filter__ = before_filter
        pass

    def raw_filter(self, raw: str):
        self.__raw_filter__ = raw

    def where(self, _tuple_):
        """
        :param _tuple_: List[[key, operator, value]]
        :return:
        """
        self.filter_dict = {}
        self.filter_clause = ""
        self.sort_clause = ""
        self.limit_clause = ""

        if not _tuple_:
            return self

        for _, v in enumerate(_tuple_):
            value = v[2]

            value = self.resolve_value(value)

            self.update_filter_dict(v, value)

        self.format_method()
        return self

    def format_method(self):
        self.filter_clause = self.filter_clause[:-4]

    def update_filter_dict(self, data, value):
        self.filter_clause += 'doc.' + data[0] + ' ' + data[1] \
                              + ' ' + str(value) + ' and '
        self.filter_dict[data[0]] = str(data[2])

    def resolve_value(self, value):
        if isinstance(value, bool):
            value = value.__str__().lower()
        elif isinstance(value, str):
            value = '"' + value + '"'
        elif isinstance(value, list):
            value = ["'" + x + "'" for x in value]
            value = '[' + ",".join(value) + ']'
        elif value is None:
            value = 'null'
        return value

    def to_dict(self):
        return self.filter_dict

    def to_aql(self, get_count=False):
        self.set_aql_query()
        if len(self.__before_filter__) > 0:
            self.aql_query += self.__before_filter__

        if get_count and len(self.filter_clause) == 0:
            return f"RETURN COUNT({self.aql_query} return 1)"

        if len(self.filter_clause) == 0:
            return self.aql_query + self.sort_clause + ' return doc'

        self.aql_query += ' filter '

        if len(self.__raw_filter__) > 0:
            if len(self.filter_clause.strip()) > 0:
                self.filter_clause += " and "

            self.filter_clause += self.__raw_filter__ + " "

        if get_count:
            return f"RETURN COUNT({self.aql_query} {self.filter_clause} return 1)"

        return self.aql_query \
               + self.filter_clause \
               + self.sort_clause \
               + self.limit_clause \
               + ' return doc'

    @staticmethod
    def get_base_dict(data) -> dict:
        return {
            "_id": data.get('_id'),
            "object_id": data.get('_key'),
            "data": data.get('data'),
            "is_active": data.get('is_active'),
            "created_at": data.get('created_at'),
            "updated_at": data.get('updated_at'),
            "created_by": data.get('created_by'),
            "updated_by": data.get('updated_by')
        }

    def _update_data(self, **kwargs):
        data = copy.deepcopy(self.data) or {}
        data.update(kwargs)
        self.data = data

    @abc.abstractmethod
    def asdict(self, *args, **kwargs) -> dict:
        pass

    def find(self, key):
        cursor = self.db.find({'_key': key})
        for x in cursor:
            return x
        return None

    def get_iterable_items(self):
        dict_items = self.asdict()
        result_dict = {}
        for _, v in dict_items.items():
            if v is not None:
                result_dict[_] = v

        return result_dict

