import abc


class CachingInterface:
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get(self, key, default=None):
        """
        Get a key from cache
        :param key:
        :param default:
        :return:
        """
        pass

    @abc.abstractmethod
    def set(self, key, value, expiry=None):
        """
        Set Key in cache
        :param expiry:
        :param key:
        :param value:
        :return:
        """
        pass

    @abc.abstractmethod
    def delete(self, key):
        """
        Delete key from cache
        :param key:
        :return:
        """
        pass

    @abc.abstractmethod
    def pluck(self, key):
        """
        Get key and then Delete from cache
        :param key:
        :return:
        """
        pass

    @abc.abstractmethod
    def flush(self):
        """
        Flush cache. Deletes all cache
        :return:
        """
        pass

    @abc.abstractmethod
    def grace_full_get(self, key, value):
        """
        If key exists return the value else set the value
        :param value:
        :param key:
        :return:
        """
        pass

    @abc.abstractmethod
    def forever(self, key, value):
        """
        If key exists return the value else set the value
        :param value:
        :param key:
        :return:
        """
        pass

    @abc.abstractmethod
    def delete_pattern(self, key_pattern):
        """
        Delete key with a pattern
        :param key_pattern:
        :return:
        """
        pass

    @abc.abstractmethod
    def keys(self, key_pattern):
        """
        get keys with specific pattern
        :param key_pattern:
        :return:
        """
        pass
