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
import src.frontend

spider_list = (Aol, Ask, Bing, Google, Mojeek)

Database.initialize()

process = CrawlerProcess()


def crawl(spiders, query, inner_crawl: bool):
    spider_names = list()
    for spider in spiders:
        util.fill_start_urls_list(spider, query)
        spider_names.append(spider.name)

    for spider in spiders:
        process.crawl(spider)

    src.frontend.logger.info(f"Crawl has started: SE: ({', '.join(spider_names)}) - "
                             f"KW: ({', '.join(query)}) - Inner: ({inner_crawl})")

    process.start()

    if inner_crawl:
        src.frontend.logger.info("Inner Crawl has started.")
        subprocess.call('PYTHONPATH=/app/ python3 /app/src/second_crawl.py', shell=True)
    src.frontend.logger.info("Crawl has ended.")


def endpoint_crawler(spiders=spider_list, query=Database.get_keywords("crawl_keys"), inner_crawl=True):
    p = Process(target=crawl, args=(spiders, query, inner_crawl))
    p.start()
    p.join()
