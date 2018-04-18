import yaml
import os


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG = yaml.load(open(os.path.join(ROOT, 'etc', 'config.yaml')))