from datetime import datetime

from flask_bcrypt import check_password_hash, generate_password_hash
from flask_login import UserMixin

from src.frontend import flask_db


class Endpoints(flask_db.Document):
    meta = {'collection': 'endpoints'}
    url = flask_db.StringField()
    domain = flask_db.StringField()
    date_created = flask_db.DateTimeField(default=datetime.utcnow())
    date_checked = flask_db.DateTimeField(default=datetime.utcnow())
    date_alive = flask_db.DateTimeField(default=datetime.utcnow())
    up_now = flask_db.BooleanField()
    tag = flask_db.StringField()
    spider = flask_db.StringField()
    keyword = flask_db.StringField()
    page = flask_db.IntField()


class Logs(flask_db.Document):
    meta = {'collection': 'logs'}
    name = flask_db.StringField()
    message = flask_db.StringField()
    time = flask_db.DateTimeField(default=datetime.utcnow())
    funcName = flask_db.StringField()
    levelname = flask_db.StringField()
    levelno = flask_db.IntField()
    filename = flask_db.StringField()
    pathname = flask_db.StringField()
    module = flask_db.StringField()
    username = flask_db.StringField()
    host = flask_db.StringField()
    msg = flask_db.StringField()
    args = flask_db.ListField()
    thread = flask_db.IntField()
    threadName = flask_db.StringField()
    process = flask_db.IntField()
    processName = flask_db.StringField()
    lineno = flask_db.IntField()
    created = flask_db.DecimalField()
    msecs = flask_db.DecimalField()
    relativeCreated = flask_db.DecimalField()
    exc_info = flask_db.StringField()
    exc_text = flask_db.StringField()
    stack_info = flask_db.StringField()


class User(UserMixin, flask_db.Document):
    meta = {'collection': 'users'}
    username = flask_db.StringField(unique=True, nullable=False)
    password = flask_db.StringField(default=True, nullable=False)
    active = flask_db.BooleanField(default=True)

    def __repr__(self):
        return f'<User {self.username}>'

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def change_pass(self, password):
        self.password = generate_password_hash(password).decode()

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False
