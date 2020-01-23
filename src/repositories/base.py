import abc
import copy
import json
from arango.database import TransactionDatabase
from sqlalchemy import func
from skeletor import db, doc
from skeletor.utility.logger import Logger
from skeletor.utility.caching.base_cache import Caching
from skeletor.utility.caching.caching_interface import CachingInterface
from skeletor.utility.json_validator import JSONSchemaValidator


class Base(object):
    model = None
    _schema = None
    __metaclass__ = abc.ABCMeta
    cache: CachingInterface = Caching().db
    __db__: TransactionDatabase = None
    logger = None

    def __init__(self, *args, **kwargs):
        self._schema = self.schema
        self.logger = Logger().get(self.__class__.__name__)

    def validate_data(self, data):
        return JSONSchemaValidator.draft_validator(self.schema, data)

    @staticmethod
    def push_to_elastic(model_instance, delete=False):
        from src.repositories.elastic_default import DefaultRepo
        if model_instance and model_instance.es_name is None or model_instance is None or not model_instance:
            return
        if delete:
            DefaultRepo().delete_by_id(
                {model_instance.es_name: [model_instance._id]})
            return
        __data = {
            **model_instance.asdict(),
            **{'id': model_instance._id}
        }

        if '_id' in __data:
            __data.pop('_id')
        if 'is_active' in __data and isinstance(__data['is_active'], bool):
            __data['is_active'] = 'TRUE' if __data['is_active'] else 'FALSE'
        DefaultRepo().populate_product({model_instance.es_name: __data})
        pass

    @staticmethod
    def validate_data_schema(data, schema):
        return JSONSchemaValidator.draft_validator(schema, data)

    def max(self, column):
        """
        Get max of a models column
        :param column:
        :return:
        """
        return db.session.query(func.max(getattr(self.model, column))).scalar()

    @property
    @abc.abstractmethod
    def schema(self):
        pass

    def get_from_cache(self, key):
        return self.cache.get(self.get_cache_name() + ":" + key)

    def store_in_cache(self, key, value):
        self.cache.forever(self.get_cache_name() + ":" + key, value)

    def evict_cache(self, key=None, pattern=None):
        if key is not None:
            self.cache.delete(self.get_cache_name() + ":" + key)
            return

        if pattern is None:
            pattern = "*"
        self.cache.delete_pattern(self.get_cache_name() + pattern)

    def get_cache_name(self):
        return self.__class__.__name__

    def store_in_cache_elastic(self, key, value):
        self.store_in_cache(key, value)
        self.push_to_elastic(value)
        pass

    def read_through_cache_elastic(self, **kwargs):
        if not self.model:
            return None

        key = json.dumps(kwargs)
        cached = self.get_from_cache(key)
        if cached is not None:
            return cached

        res = self.model.query.filter_by(**kwargs).first()
        self.store_in_cache_elastic(key, res)
        return res

    def read_through_cache_multi(self, **kwargs):
        if not self.model:
            return None

        key = json.dumps(kwargs)
        cached = self.get_from_cache(key)
        if cached is not None:
            return cached

        result = self.model.query.filter_by(**kwargs).all()
        self.store_in_cache(key, result)
        return result

    def read_through_cache(self, **kwargs):
        if not self.model:
            return None

        key = json.dumps(kwargs)
        cached = self.get_from_cache(key)
        if cached is not None:
            return cached
        res = self.model.query.filter_by(**kwargs).first()
        self.store_in_cache(key, res)
        return res

    def delete_es_index(self):
        from src.repositories.elastic_base import ElasticInsertRepo
        search = ElasticInsertRepo()
        instance__ = self.get_es_model_instance()
        if not instance__.es_name:
            return
        if search.index_exits(instance__.es_name + "_index"):
            search.delete_index(instance__.es_name + "_index")
        return True

    def create_es_index(self):
        from src.repositories.elastic_base import ElasticInsertRepo
        search = ElasticInsertRepo()
        instance__ = self.get_es_model_instance()
        if not instance__.es_name:
            return
        if not search.index_exits(instance__.es_name + "_index"):
            __mappings = instance__.get_es_index_mapping()
            search.create_index(
                instance__.es_name +
                "_index",
                instance__.es_name,
                __mappings)
        return True

    def get_paginated_query(self):
        return self.model.query.paginate(
            page=1, max_per_page=10, error_out=False)

    def get_es_model_instance(self):
        from importlib import import_module
        return getattr(
            import_module(
                self.model.__module__),
            self.model.__name__)()

    def transform(self, instance):
        return instance

    def reindex_elastic(self):
        # drop index and recreate index
        from src.repositories.elastic_base import ElasticInsertRepo
        search = ElasticInsertRepo()
        instance__ = self.get_es_model_instance()
        if not instance__.es_name:
            return
        self.evict_cache()
        if not search.index_exits(instance__.es_name + "_index"):
            __mappings = instance__.get_es_index_mapping()
            search.create_index(
                instance__.es_name +
                "_index",
                instance__.es_name,
                __mappings)

        res = self.get_paginated_query()
        while True:
            if not res.items:
                break
            for x in res.items:
                self.push_to_elastic(self.transform(x))
                pass
            res = res.next()
            pass
        pass

    def get_query_filters(self, **kwargs):
        return None

    @staticmethod
    def get_paginate_params(**kwargs):
        data = copy.deepcopy(kwargs)
        size = data.pop('size', 10)
        page = data.pop('page')
        if page == 1:
            page = 0
            pass
        if page > 1:
            page = size * (page - 1)
            pass
        return page, size


class ArangoRepoBase(Base):
    @property
    def schema(self):
        return {}

    def get_query_filters(self, **kwargs):
        return []

    def paginate_count(self, **kwargs):
        data = copy.deepcopy(kwargs)
        data.pop('size', 0)
        data.pop('page', 0)
        __filter = self.get_query_filters(**data)
        query = self.model.where(__filter)
        _query = query.to_aql(True)
        Logger.log(Logger.INFO, f"[AQL QUERY] {_query}")
        cursor = self.model.aql.execute(_query)
        for x in cursor:
            return x
        return 0
