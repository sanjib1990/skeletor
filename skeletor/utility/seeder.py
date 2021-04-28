def call_all_seeders():
    import os
    from importlib import import_module

    path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'seeders'))
    for directory, subdirectories, files in os.walk(path):
        files.sort()
        for file in files:
            if file.endswith('.py'):
                module = 'seeders.' + file[:-3]
                mod = import_module(module)
                run = getattr(mod, 'run')
                print('SEEDING: ' + module)
                run()
                pass
            pass
        pass
    pass


def seed_db():
    call_all_seeders()

