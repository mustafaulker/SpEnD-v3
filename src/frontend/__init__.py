from flask import Flask
from flask_apscheduler import APScheduler
from flask_login import LoginManager
from flask_mail import Mail
from flask_mongoengine import MongoEngine
from flask_recaptcha import ReCaptcha
from scrapy.crawler import CrawlerProcess

from src.SpEnD.spiders.aol import Aol
from src.SpEnD.spiders.ask import Ask
from src.SpEnD.spiders.bing import Bing
from src.SpEnD.spiders.google import Google
from src.SpEnD.spiders.mojeek import Mojeek
from src.utils.sparql_controller import Sparql

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

process = CrawlerProcess()

search_engine_dict = {
    "Google": Google,
    "Bing": Bing,
    "Ask": Ask,
    "Mojeek": Mojeek,
    "Aol": Aol
}

scheduler = APScheduler()

scheduler.add_job(id='endpoint_check', func=Sparql.check_endpoints, trigger="interval", minutes=30)
scheduler.start()

from src.frontend import models
from src.frontend import routes
from src.frontend import errors
