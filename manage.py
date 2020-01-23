import warnings
from skeletor import load_urls
from flask_script import Manager, Command, Shell, Server

warnings.filterwarnings('ignore')


class SyncDB(Command):
    def run(self):
        from skeletor import db
        db.create_all()


class AppShell(Shell):
    def run(self, no_ipython=False, no_bpython=False, no_ptipython=False, no_ptpython=False):

        app.debug = app.config['DEBUG']
        app.secret_key = app.config['SECRET_KEY']

        context = self.get_context()
        if not no_ipython:
            try:
                from IPython.terminal.embed import InteractiveShellEmbed, embed
                try:
                    embed(banner1=self.banner, user_ns=context)
                except AttributeError:
                    sh = InteractiveShellEmbed(banner1=self.banner)
                    sh(global_ns=dict(), local_ns=context)
                return
            except ImportError:
                pass


class AppServer(Server):
    def __call__(self, app, host, port, use_debugger, use_reloader,
                 threaded, processes, passthrough_errors, ssl_crt, ssl_key, **options):

        host, port = app.config['SERVER_HOST_NAME'].split(":")
        app.debug = app.config['DEBUG']
        app.secret_key = app.config['SECRET_KEY']
        print(">>> SECRET: %s <<<" % app.secret_key)
        load_urls(app)
        super(AppServer, self).__call__(app, host, port, use_debugger, True,
                                       threaded, processes, passthrough_errors, None, None)


if __name__ == '__main__':
    from skeletor import app, migrate
    from flask_migrate import MigrateCommand
    manager = Manager(app)
    manager.add_command('runserver', AppServer())
    manager.add_command('shell', AppShell())
    manager.add_command('syncdb', SyncDB())
    manager.add_command('db', MigrateCommand)
    manager.run()
