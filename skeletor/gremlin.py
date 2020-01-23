from skeletor.utility.decorators import singleton
from skeletor.utility.exceptions.general_error import GeneralException
from skeletor.utility.logger import Logger
from gremlin_python.process.anonymous_traversal import traversal
from gremlin_python.process.graph_traversal import GraphTraversalSource
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection

__g_db_pool__ = None


@singleton
class GremlinConnector(object):
    __app__ = None

    logger = None

    def __init__(self, **kwargs):
        if 'app' not in kwargs:
            raise GeneralException(message="app instance is required")

        self.__app__ = kwargs['app']
        self.logger = Logger().get(self.__class__.__name__)

    def __get_connection__(self):
        global __g_db_pool__

        if __g_db_pool__ is None:
            connection_properties = {
                "url": self.__app__.config['GREMLIN_URI'],
                "traversal_source": 'g',
                "pool_size": self.__app__.config['GREMLIN_POOL_SIZE'],
                "max_workers": self.__app__.config['GREMLIN_MAX_WORKERS']
            }
            __g_db_pool__ = DriverRemoteConnection(**connection_properties)
            self.logger.info('Connected to {}'.format(self.__app__.config['GREMLIN_URI']))
            self.logger.info('Initialized graph db pool')

        return __g_db_pool__

    def get_traversal(self) -> GraphTraversalSource:
        return traversal().withRemote(self.__get_connection__())
