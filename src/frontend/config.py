class Config(object):
    DEBUG = True
    DEVELOPMENT = True
    SECRET_KEY = 'super-secret-key'
    FLASK_SECRET = SECRET_KEY
    DB_HOST = 'database'  # a docker link


class MongoConfig(Config):
    MONGODB_HOST = 'localhost'
    MONGODB_PORT = 27017
    MONGODB_DB = 'frontend'


class MailConfig(Config):
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = 465,
    MAIL_USE_SSL = True,
    MAIL_USERNAME = '-',
    MAIL_PASSWORD = '-',
    MAIL_RECIPIENTS = ['-', '-']
