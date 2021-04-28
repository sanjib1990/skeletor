from elasticsearch import Elasticsearch
from flask import Flask, request, session, g
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from .arango import ArangoDB
from .config import ELASTICSEARCH_URI, ENV, DATABASES
from .elasticsearch import ElasticsearchConnection
from .gremlin import GremlinConnector
from .postgress import PostGressConnection
from .utility.redis_session import RedisSessionInterface
from .utility.regex_converter import RegexConverter
from .utility.renderers import JSONRenderer
from .utility.url_loader import load_urls

app = Flask(__name__)
app.config.from_object('skeletor.config')
app.config['JSON_SORT_KEYS'] = False
app.session_interface = RedisSessionInterface(conf=app.config['CACHES'])
app.url_map.converters['regex'] = RegexConverter

sentry = None

# arango connector
doc = ArangoDB()

# connect to postgress during initall loading
db = PostGressConnection(app=app).get()

# connect to graph through gremlin
graph = GremlinConnector(app=app)

# connect elastic search
es = ElasticsearchConnection(app=app).get()

# the following line for models is required to load all the models
from src import models

cors = CORS(app)

# only wait for 1 second, regardless of the client's default
if ENV != 'local':
    es.cluster.health(wait_for_status='yellow', request_timeout=1)

migrate = Migrate(app, db)

app.config['ARANGO_DATABASE'] = DATABASES['arango']
app.config['PROPAGATE_EXCEPTIONS'] = True
doc.init_app(app)

from skeletor.utility.logger import Logger
app.logger = Logger().get(__name__)


def before_send(event, hint):
    if 'exc_info' in hint:
        exc_type, exc_value, tb = hint['exc_info']
        if hasattr(exc_value, 'report') and not exc_value.report:
            return None
    return event


@app.before_request
def before_request(*args, **kwargs):
    session.permanent = False
    user = session.get('user', None)
    if user:
        app.logger.info('{log_type} {user} [{method}] {url}'.format(
            log_type="request_logging",
            user=user.get('email'),
            method=request.method,
            url=request.url
        ))

    app.logger.info(f'[REQUEST_BODY] {request.get_data().decode()}')


@app.errorhandler(404)
def api_404_handler(e):
    return api_error_handler(e, 404)


@app.errorhandler(Exception)
def api_error_handler(e, code=500):
    renderer = JSONRenderer()
    message = "Internal Server Error"
    validation = []

    if hasattr(e, 'error_dict'):
        if 'code' in e.error_dict:
            code = e.error_dict.get('code')
        if 'message' in e.error_dict:
            message = e.error_dict.get('message')
        if 'validation' in e.error_dict:
            validation = e.error_dict.get('validation')

    if isinstance(str(e), str) and len(str(e).strip()) > 0:
        message = str(e)

    app.logger.info('{0}: {1}'.format(message, e))
    data = {
        "message": message,
        'errors': validation
    }

    if sentry:
        data["event_id"] = g.sentry_event_id

    return renderer.render(data, code)

