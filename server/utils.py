import yaml
import os
import logging

from logging.handlers import RotatingFileHandler

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG = yaml.load(open(os.path.join(ROOT, 'etc', 'config.yaml')))

access_log = logging.getLogger('tornado.access')
app_log = logging.getLogger('tornado.application')
gen_log = logging.getLogger('tornado.general')

access_handler = RotatingFileHandler(os.path.join(ROOT, 'logs', 'access.log'), maxBytes=2048, backupCount=5)
app_handler = RotatingFileHandler(os.path.join(ROOT, 'logs', 'app.log'), maxBytes=2048, backupCount=5)
gen_handler = RotatingFileHandler(os.path.join(ROOT, 'logs', 'gen.log'), maxBytes=2048, backupCount=5)

access_log.addHandler(access_handler)
access_log.setLevel(logging.DEBUG)

app_log.addHandler(app_handler)
app_log.setLevel(logging.DEBUG)

gen_log.addHandler(gen_handler)