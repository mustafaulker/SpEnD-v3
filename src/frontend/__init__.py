import logging

from flask import Flask
from flask_apscheduler import APScheduler
from flask_login import LoginManager
from flask_mongoengine import MongoEngine
from mongolog.handlers import MongoHandler

from src.utils.database_controller import Database

# pymongo object
db = Database.instance()

from src.SpEnD.spiders.aol import Aol
from src.SpEnD.spiders.ask import Ask
from src.SpEnD.spiders.bing import Bing
from src.SpEnD.spiders.google import Google
from src.SpEnD.spiders.mojeek import Mojeek
import src.main_crawl
from src.frontend.config import MongoConfig
from src.utils.sparql_controller import Sparql

app = Flask(__name__)
app.config.from_object('src.frontend.config')
app.config.from_object('src.frontend.config.MongoConfig')

# flask_mongoengine object
flask_db = MongoEngine(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

search_engine_dict = {
    "Google": Google,
    "Bing": Bing,
    "Ask": Ask,
    "Mojeek": Mojeek,
    "Aol": Aol
}

scheduler = APScheduler()

scheduler.add_job(id='status_check', func=Sparql.check_endpoints, trigger="interval", hours=1)
scheduler.add_job(id='auto_crawl', func=src.main_crawl.endpoint_crawler, trigger="interval", days=1)
scheduler.start()

logger = logging.getLogger(__name__)
logger.addHandler(MongoHandler.to(db='SpEnD-DB', collection='logs', host=MongoConfig.MONGODB_HOST,
                                  port=MongoConfig.MONGODB_PORT))

from src.frontend import models
from src.frontend import routes
from src.frontend import errors
