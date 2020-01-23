from os import listdir
from os.path import isfile, join
import importlib
import traceback


# Load the URLS from urls.py
def load_urls(app):
    modules_list = []
    routes = join(app.config["BASE_DIR"], "src", "routes")
    for path in listdir(routes):
        if isfile(join(routes, path)):
            path, _ = path.split('.')
            if path != '__init__':
                modules_list.append(path)
    for module in modules_list:
        try:
            blueprint = getattr(
                importlib.import_module("src.routes.%s" % module),
                'blueprint', None
            )
            if blueprint:
                app.register_blueprint(blueprint)
            print("Imported: src.routes.%s" % module)
        except Exception as e:
            print(traceback.format_exc())
            print("Unimported: src.routes.%s" % module, e)
