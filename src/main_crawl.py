import subprocess
from multiprocessing import Process

from scrapy.crawler import CrawlerProcess

from src.SpEnD.spiders.aol import Aol
from src.SpEnD.spiders.ask import Ask
from src.SpEnD.spiders.bing import Bing
from src.SpEnD.spiders.google import Google
from src.SpEnD.spiders.mojeek import Mojeek
from src.utils import util
from src.utils.database_controller import Database

spiders = [Aol, Ask, Bing, Google, Mojeek]

Database.initialize()

process = CrawlerProcess()


def crawl(spiders, query):
    for spider in spiders:
        util.fill_start_urls_list(spider, query)

    for spider in spiders:
        process.crawl(spider)

    process.start()

    subprocess.call('PYTHONPATH=/app/ python3 /app/src/second_crawl.py', shell=True)


def endpoint_crawler(spiders=spiders, query=Database.get_keywords("crawl_keys")):
    p = Process(target=crawl, args=(spiders, query))
    p.start()
    p.join()
