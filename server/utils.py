import yaml
import os
import logging

from logging.handlers import RotatingFileHandler
from datetime import date, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_PATH = os.path.join(ROOT, 'frontend', 'dist')
CONFIG = {
    'server': {
        'host': os.getenv('HOST', '0.0.0.0'),
        'port': os.getenv('PORT', '9989')
    },
    'db': {
        'host': 'postgresdb',
        'dbname': os.getenv('POSTGRES_DB', 'postgres'),
        'user': os.getenv('POSTGRES_USER', 'python'),
        'password': os.getenv('POSTGRES_PASSWORD', 'python'),
        'port': 5432
    }
}

LOGGING_LEVEL = logging.DEBUG
MAX_LIMIT = 100
DEFAULT_LIMIT = 30

fmt = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

access_log = logging.getLogger('tornado.access')
app_log = logging.getLogger('tornado.application')
gen_log = logging.getLogger('tornado.general')

access_handler = RotatingFileHandler(os.path.join(ROOT, 'logs', 'access.log'), maxBytes=2 * 1024 ** 2, backupCount=5)
access_handler.setFormatter(fmt)
app_handler = RotatingFileHandler(os.path.join(ROOT, 'logs', 'app.log'), maxBytes=2 * 1024 ** 2, backupCount=5)
app_handler.setFormatter(fmt)
gen_handler = RotatingFileHandler(os.path.join(ROOT, 'logs', 'gen.log'), maxBytes=2 * 1024 ** 2, backupCount=5)
gen_handler.setFormatter(fmt)

access_log.addHandler(access_handler)
access_log.setLevel(LOGGING_LEVEL)

app_log.addHandler(app_handler)
app_log.setLevel(LOGGING_LEVEL)

gen_log.addHandler(gen_handler)


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.strftime("%H:%M:%S %Y-%m-%d")
    raise TypeError ("Type %s not serializable" % type(obj))
