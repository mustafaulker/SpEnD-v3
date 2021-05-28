from datetime import datetime

from flask_bcrypt import check_password_hash, generate_password_hash
from flask_login import UserMixin

from src.frontend import db


class Endpoints(db.Document):
    meta = {'collection': 'endpoints'}
    url = db.StringField()
    domain = db.StringField()
    date_created = db.DateTimeField(default=datetime.utcnow())
    date_checked = db.DateTimeField(default=datetime.utcnow())
    date_alive = db.DateTimeField(default=datetime.utcnow())
    up_now = db.BooleanField()
    tag = db.StringField()
    spider = db.StringField()
    keyword = db.StringField()
    page = db.IntField()


class Logs(db.Document):
    meta = {'collection': 'logs'}
    name = db.StringField()
    message = db.StringField()
    time = db.DateTimeField(default=datetime.utcnow())
    funcName = db.StringField()
    levelname = db.StringField()
    levelno = db.IntField()
    filename = db.StringField()
    pathname = db.StringField()
    module = db.StringField()
    username = db.StringField()
    host = db.StringField()
    msg = db.StringField()
    args = db.ListField()
    thread = db.IntField()
    threadName = db.StringField()
    process = db.IntField()
    processName = db.StringField()
    lineno = db.IntField()
    created = db.DecimalField()
    msecs = db.DecimalField()
    relativeCreated = db.DecimalField()
    exc_info = db.StringField()
    exc_text = db.StringField()
    stack_info = db.StringField()


class User(UserMixin, db.Document):
    meta = {'collection': 'users'}
    username = db.StringField(unique=True, nullable=False)
    password = db.StringField(default=True, nullable=False)
    active = db.BooleanField(default=True)

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
