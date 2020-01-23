from skeletor import app
from skeletor.utility.caching.caching_interface import CachingInterface
from skeletor.utility.caching.redis_cache import RedisCache
from skeletor.utility.exceptions.general_error import GeneralException


class Caching:
    db: CachingInterface = None

    def __init__(self, *args, **kwargs):
        self.default_cache_driver = app.config['DEFAULT_CACHE_DRIVER']
        self.set_handler()

    def set_handler(self):
        if self.default_cache_driver == 'redis':
            self.db = RedisCache(**app.config['CACHE_DRIVERS']['redis'])
        else:
            raise GeneralException(message="Default cache driver not defined.")

