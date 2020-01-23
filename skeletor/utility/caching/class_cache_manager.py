from typing import List
from skeletor.utility.caching.base_cache import Caching
from skeletor.utility.caching.cachable import Cachable
from skeletor.utility.caching.caching_interface import CachingInterface


class ClassCacheManager:
    cache: CachingInterface

    def __init__(self):
        self.cache = Caching().db

    def set(self, value: Cachable):
        self.cache.set(
            self.__get_key(value, getattr(value, value.cache_key)),
            value
        )

    def __get_key(self, cls, identity):
        print(cls, identity)
        return cls.cls_cache_name() + ':' + cls.cache_key + ':' + identity

    def get(self, cls, key):
        self.cache.get(self.__get_key(cls, key))

    def set_all(self, values: List[Cachable]):
        for _, v in enumerate(values):
            self.set(v)
