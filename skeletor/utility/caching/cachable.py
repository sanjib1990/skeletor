import abc


class Cachable:
    __metaclass__ = abc.ABCMeta

    def cls_cache_name(self):
        return self.__class__.__name__

    @property
    @abc.abstractmethod
    def cache_key(self):
        pass
