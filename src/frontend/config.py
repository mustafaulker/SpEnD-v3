class Config(object):
    DEBUG = True
    DEVELOPMENT = True
    SECRET_KEY = 'super-secret-key'
    FLASK_SECRET = SECRET_KEY
    DB_HOST = 'database'  # a docker link


class MongoConfig(Config):
    MONGODB_HOST = 'mongo'
    MONGODB_PORT = 27017
    MONGODB_DB = 'SpEnD-DB'


class MailConfig(Config):
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = '-'
    MAIL_PASSWORD = '-'
    MAIL_RECIPIENTS = ['-', '-']


class ReCaptchaConfig(Config):
    RECAPTCHA_ENABLED = True
    # Test keys
    RECAPTCHA_SITE_KEY = "6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI"
    RECAPTCHA_SECRET_KEY = "6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe"
    RECAPTCHA_THEME = "light"
    RECAPTCHA_TYPE = "image"
    RECAPTCHA_SIZE = "normal"
