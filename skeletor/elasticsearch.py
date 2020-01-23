from elasticsearch import Elasticsearch
from skeletor import ELASTICSEARCH_URI
from skeletor.utility.decorators import singleton


@singleton
class ElasticsearchConnection(object):
    __db__: Elasticsearch = None

    def __init__(self, *args, **kwargs):
        if 'app' in kwargs:
            self.__db__ = Elasticsearch(
                ELASTICSEARCH_URI,
                timeout=30,
                max_retries=10,
                retry_on_timeout=True
            )

    def get(self) -> Elasticsearch:
        return self.__db__
