import os

from src.SpEnD.spiders.aol import Aol
from src.SpEnD.spiders.ask import Ask
from src.SpEnD.spiders.bing import Bing
from src.SpEnD.spiders.google import Google
from src.SpEnD.spiders.mojeek import Mojeek
from src.utils import util
from src.utils.database_controller import Database
from src.frontend import process

spiders = [Aol, Ask, Bing, Google, Mojeek]
Database.initialize()


def crawl(spiders=spiders, query=Database.get_keywords("crawl_keys")):

    for spider in spiders:
        util.fill_start_urls_list(spider, query)

    for spider in spiders:
        process.crawl(spider)

    process.start()
    os.system("python second_crawl.py")
