from datetime import datetime

from flask_bcrypt import check_password_hash
from flask_login import UserMixin
from src.frontend import db


class Endpoints(db.Document):
    url = db.StringField()
    domain = db.StringField()
    date_created = db.DateTimeField(default=datetime.now())
    date_checked = db.DateTimeField(default=datetime.now())
    date_alive = db.DateTimeField(default=datetime.now())
    up_now = db.BooleanField()
    tag = db.StringField()


class Keywords(db.Document):
    crawl_keys = db.DictField()
    second_crawl_keys = db.DictField()
    wanted_keys = db.DictField()
    unwanted_keys = db.DictField()


class User(UserMixin, db.Document):
    meta = {'collection': 'users'}
    username = db.StringField(unique=True)
    password = db.StringField(default=True)
    active = db.BooleanField(default=True)

    def __repr__(self):
        return f'<User {self.username}>'

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False
