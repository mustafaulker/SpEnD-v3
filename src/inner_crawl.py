from scrapy.crawler import CrawlerProcess

import src.frontend as fe
from SpEnD.spiders.aol import Aol
from SpEnD.spiders.ask import Ask
from SpEnD.spiders.bing import Bing
from SpEnD.spiders.google import Google
from SpEnD.spiders.mojeek import Mojeek
from utils import util

spiders = [Aol, Ask, Bing, Google, Mojeek]

for spider in spiders:
    util.clear_urls(spider)
    util.fill_inner_urls(spider, fe.db.get_keywords("inner_keys"))
    spider.is_first_crawl = False

process = CrawlerProcess()

for spider in spiders:
    process.crawl(spider)

process.start()
