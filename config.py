import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DASH_BASE_PATHNAME = '/app/'
    #~ WIKICHRON_DATA_DIR

class DevelopmentConfig(Config):
    APP_HOSTNAME = 'http://localhost'
    PORT = '5500'
    DEBUG = True

class ProductionConfig(Config):
    APP_HOSTNAME = 'http://wikichron.science'
    PORT = '5500'
    REDIS_URL = 'redis://localhost:6379'
    DEBUG = False
