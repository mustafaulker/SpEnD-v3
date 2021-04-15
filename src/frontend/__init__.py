from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from flask_mongoengine import MongoEngine
from flask_recaptcha import ReCaptcha

app = Flask(__name__)
app.config.from_object('src.frontend.config')
app.config.from_object('src.frontend.config.MongoConfig')
app.config.from_object('src.frontend.config.MailConfig')
app.config.from_object('src.frontend.config.ReCaptchaConfig')

db = MongoEngine(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

mail = Mail(app)

recaptcha = ReCaptcha(app)

from src.frontend import models
from src.frontend import routes
from src.frontend import errors
