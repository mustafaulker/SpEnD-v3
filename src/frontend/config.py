import os


class Config(object):
    SECRET_KEY = '50087ddf76b4ead485fd268eb3477d7b'
    FLASK_SECRET = SECRET_KEY
    STATIC_URL_PATH = '/static/'
    STATIC_FOLDER = 'static'
    TEMPLATE_FOLDER = 'templates'


class MongoConfig(Config):
    MONGODB_DB = 'SpEnD-DB'
    MONGODB_CONNECT = False
    try:
        MONGODB_HOST = os.environ["MONGODB_HOST"]
        MONGODB_PORT = int(os.environ["MONGODB_PORT"])
    except:
        MONGODB_HOST = 'localhost'
        MONGODB_PORT = 27017
