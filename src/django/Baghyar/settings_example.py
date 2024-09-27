import os

IS_PRODUCTION = False   # os.environ.get('IS_PRODUCTION')
IS_SQLite = True

if IS_PRODUCTION:
    from .conf.production import *
elif IS_SQLite:
    from .conf.sqlite import *
else:
    from .conf.development import *
