import os
from dotenv import load_dotenv
import logging

path = os.path.abspath(os.path.join(
    os.path.dirname(__file__),
    "..",
    ".env")
)
load_dotenv(dotenv_path=path)

ENV = os.getenv('ENV', 'local')
NAME = os.getenv("APP_NAME", "Skeletor")
DEBUG = False if ENV == 'production' else os.getenv('DEBUG', 'True') == 'True'

SECRET_KEY = '$-mry&ws#7@crlm)rahnjrk+sw@_^-l!-wwow2ku2oa9xtxo!v'

SERVER_HOST_NAME = os.getenv('SERVER_NAME', '127.0.0.1:5056')

DATABASES = {
    'postgress': {
        "NAME": os.getenv('DEFAULT_DB_NAME', 'spectre'),
        "USER": os.getenv("DEFAULT_DB_USER_NAME", 'nebula'),
        "PASSWORD": os.getenv("DEFAULT_DB_PASSWORD"),
        "HOST": os.getenv("DEFAULT_DB_HOST", "localhost"),
        "PORT": os.getenv("DEFAULT_DB_PORT", 5432),
        "PROTOCOL": os.getenv("DEFAULT_DB_PROTOCOL", "postgresql+psycopg2")
    },
    'arango': {
        "NAME": os.getenv("ARANGO_DB_NAME", 'spectre'),
        "USER": os.getenv("ARANGO_DB_USER", 'root'),
        "PASSWORD": os.getenv("ARANGO_DB_PASSWORD", ''),
        "HOST": os.getenv("ARANGO_DB_HOST", '127.0.0.1'),
        "PORT": os.getenv("ARANGO_DB_PORT", '8529'),
        "PROTOCOL": os.getenv("ARANGO_DB_PROTOCOL", 'http')
    }
}
SENTRY = os.getenv('SENTRY', None)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_LEVEL = getattr(logging, os.getenv('LOG_LEVEL', 'DEBUG'))
ELASTICSEARCH_URI = os.getenv('ELASTICSEARCH_URI', 'localhost:9200')

# Local
CACHES = {
    "HOST": os.getenv("CACHE_HOST", 'localhost'),
    "PORT": os.getenv("CACHE_PORT", '6379'),
    "DB": os.getenv("CACHE_DB", 4)
}

DEFAULT_CACHE_DRIVER = os.getenv("DEFAULT_CACHE_DRIVER", 'redis')
CACHE_DRIVERS = {
    'redis': {
        "HOST": CACHES.get('HOST'),
        "PORT": CACHES.get('PORT'),
        "DB": CACHES.get('DB'),
        "KEY_PREFIX": NAME + ':' + ENV + ':',
        "TIMEOUT": 86400
    }
}

DATE_TIME_FORMAT = os.getenv('DATE_TIME_FORMAT', '%Y-%m-%d %H:%M:%S')

GREMLIN_URI = os.getenv('GREMLIN_URI', 'ws://localhost:8182/gremlin')
GREMLIN_POOL_SIZE = int(os.getenv('GREMLIN_POOL_SIZE', 4))
GREMLIN_MAX_WORKERS = int(os.getenv('GREMLIN_MAX_WORKERS', 4))

SQLALCHEMY_DATABASE_URI = f'{DATABASES["postgress"]["PROTOCOL"]}' \
                          f'://{DATABASES["postgress"]["USER"]}' \
                          f':{DATABASES["postgress"]["PASSWORD"]}' \
                          f'@{DATABASES["postgress"]["HOST"]}' \
                          f':{DATABASES["postgress"]["PORT"]}' \
                          f'/{DATABASES["postgress"]["NAME"]}'
SQLALCHEMY_TRACK_MODIFICATIONS = True
