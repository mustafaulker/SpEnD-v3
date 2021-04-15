from scrapy.crawler import CrawlerProcess
from SpEnD.spiders.aol import Aol
from SpEnD.spiders.ask import Ask
from SpEnD.spiders.bing import Bing
from SpEnD.spiders.google import Google
from SpEnD.spiders.mojeek import Mojeek
from SpEnD.spiders.yippy import Yippy
from utils import util
from utils.database_controller import Database
import os
import schedule
import time


def crawl():
    spiders = [Aol, Ask, Bing, Google, Mojeek, Yippy]
    Database.initialize()

    for spider in spiders:
        util.fill_start_urls_list(spider, Database.get_keywords("crawl_keys"))

    process = CrawlerProcess()

    for spider in spiders:
        process.crawl(spider)

    process.start()
    os.system("python second_crawl.py")


schedule.every().day.at("00:00").do(crawl)

while True:
    schedule.run_pending()
    time.sleep(1)
