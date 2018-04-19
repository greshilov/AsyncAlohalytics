import yaml
import os
import logging

from logging.handlers import RotatingFileHandler
from datetime import date, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_PATH = os.path.join('frontend', 'dist')
CONFIG = yaml.load(open(os.path.join(ROOT, 'etc', 'config.yaml')))
LOGGING_LEVEL = logging.DEBUG

access_log = logging.getLogger('tornado.access')
app_log = logging.getLogger('tornado.application')
gen_log = logging.getLogger('tornado.general')

access_handler = RotatingFileHandler(os.path.join(ROOT, 'logs', 'access.log'), maxBytes=2 * 1024 ** 2, backupCount=5)
app_handler = RotatingFileHandler(os.path.join(ROOT, 'logs', 'app.log'), maxBytes=2 * 1024 ** 2, backupCount=5)
gen_handler = RotatingFileHandler(os.path.join(ROOT, 'logs', 'gen.log'), maxBytes=2 * 1024 ** 2, backupCount=5)

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