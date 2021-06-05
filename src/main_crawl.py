import subprocess
from multiprocessing import Process

from scrapy.crawler import CrawlerProcess

import src.frontend as fe
from src.SpEnD.spiders.aol import Aol
from src.SpEnD.spiders.ask import Ask
from src.SpEnD.spiders.bing import Bing
from src.SpEnD.spiders.google import Google
from src.SpEnD.spiders.mojeek import Mojeek
from src.utils import util

spider_list = (Aol, Ask, Bing, Google, Mojeek)

process = CrawlerProcess()


def crawl(spiders, query, inner_crawl: bool):
    spider_names = list()
    for spider in spiders:
        util.fill_start_urls_list(spider, query)
        spider_names.append(spider.name)

    for spider in spiders:
        process.crawl(spider)

    fe.logger.info(f"Crawl has started: SE: ({', '.join(spider_names)}) - "
                   f"KW: ({', '.join(query)}) - Inner: ({inner_crawl})")

    process.start()

    if inner_crawl:
        fe.logger.info("Inner Crawl has started.")
        subprocess.call('PYTHONPATH=/app/ python3 /app/src/second_crawl.py', shell=True)
    fe.logger.info("Crawl has ended.")


def endpoint_crawler(spiders=spider_list, query=fe.db.get_keywords("crawl_keys"), inner_crawl=True):
    p = Process(target=crawl, args=(spiders, query, inner_crawl))
    p.start()
    p.join()
