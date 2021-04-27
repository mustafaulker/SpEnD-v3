from scrapy.crawler import CrawlerProcess

from SpEnD.spiders.aol import Aol
from SpEnD.spiders.ask import Ask
from SpEnD.spiders.bing import Bing
from SpEnD.spiders.google import Google
from SpEnD.spiders.mojeek import Mojeek
from utils import util
from utils.database_controller import Database

spiders = [Aol, Ask, Bing, Google, Mojeek]
Database.initialize()

for spider in spiders:
    util.clear_start_urls_list(spider)
    util.fill_start_urls_list_for_second_crawl(spider, Database.get_keywords("second_crawl_keys"))
    spider.is_first_crawl = False

process = CrawlerProcess()

for spider in spiders:
    process.crawl(spider)

process.start()
