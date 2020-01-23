from arango import ArangoClient
from flask import current_app, _app_ctx_stack as stack


class ArangoDB(object):
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.config.setdefault(
            'PYARANGO_DATABASE_CONF',
            app.config['ARANGO_DATABASE'])
        app.teardown_appcontext(self.teardown)

    def connect(self):
        arango_conf = current_app.config['PYARANGO_DATABASE_CONF']
        return ArangoClient(
            protocol=arango_conf['PROTOCOL'],
            host=arango_conf['HOST'],
            port=arango_conf['PORT'])

    def teardown(self, exception):
        ctx = stack.top
        if hasattr(ctx, 'arango_client'):
            # ctx.arango_client.remove()
            pass

    @property
    def client(self):
        ctx = stack.top
        if ctx is not None:
            if not hasattr(ctx, 'arango_client'):
                ctx.arango_client = self.connect()
            return ctx.arango_client
        return None

    @property
    def db(self):
        if self.client:
            arango_conf = current_app.config['PYARANGO_DATABASE_CONF']
            return self.client.db(
                arango_conf['NAME'],
                username=arango_conf['USER'],
                password=arango_conf['PASSWORD'])
        return None
