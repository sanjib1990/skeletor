import pickle
from redis import Redis
from skeletor.utility.caching.caching_interface import CachingInterface


class RedisCache(CachingInterface):
    redis = None
    expiry = None
    serializer = pickle

    def __init__(self, *args, **kwargs):
        self.redis = Redis(
            host=kwargs.get('HOST'),
            port=kwargs.get('PORT'),
            db=kwargs.get('DB'))
        self.prefix = kwargs.get('KEY_PREFIX')
        self.expiry = kwargs.get('TIMEOUT')

    def get(self, key, default=None):
        val = self.redis.get(self.prefix + key)
        if val is not None:
            return self.serializer.loads(val)

        return default

    def set(self, key, value, expiry=None):
        if expiry is None:
            expiry = self.expiry
        val = self.serializer.dumps(value)
        self.redis.setex(self.prefix + key, int(expiry), val)

    def delete(self, key):
        self.redis.delete(self.prefix + key)

    def pluck(self, key):
        val = self.get(key)
        self.delete(key)

        return val

    def flush(self):
        for x in self.redis.scan_iter(self.prefix + '*'):
            self.redis.delete(x)

    def grace_full_get(self, key, value):
        val = self.get(key)
        if val is not None:
            return val

        self.set(key, value)
        return value

    def forever(self, key, value):
        val = self.serializer.dumps(value)
        return self.redis.set(name=(self.prefix + key), value=val)

    def delete_pattern(self, key_pattern):
        _keys = self.keys(key_pattern)
        for x in _keys:
            self.redis.delete(x)

    def keys(self, key_pattern):
        val = self.redis.keys(self.prefix + key_pattern)
        if val is not None:
            return [x.decode('utf-8') for x in val]
        return []
