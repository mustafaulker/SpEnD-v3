import logging
import urllib.parse

import scrapy
from scrapy import Request

from src.utils import util
from src.utils.sparql_controller import Sparql


class Ask(scrapy.Spider):

    def __init__(self, *args, **kwargs):
        logging.getLogger("scrapy.downloadermiddlewares.redirect").setLevel(logging.INFO)
        logging.getLogger("scrapy.middleware").setLevel(logging.WARNING)
        logging.getLogger("scrapy.extensions").setLevel(logging.WARNING)
        logging.getLogger("scrapy.statscollectors").setLevel(logging.WARNING)
        logging.getLogger("scrapy.crawler").setLevel(logging.WARNING)
        super().__init__(*args, **kwargs)

    name = "ask"
    base_url = "https://www.ask.com/web?q="
    search_parameters = ""
    is_first_crawl = True

    custom_settings = {
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
        "CONCURRENT_REQUESTS": 1,
        "CONCURRENT_REQUESTS_PER_IP": 1,
        "DOWNLOAD_DELAY": 7,
    }

    start_urls = []

    def parse(self, response):
        if "&" in response.url:
            keyword = response.url[response.url.index("=") + 1:response.url.index("&")]
            keyword = urllib.parse.unquote_plus(keyword)
        else:
            keyword = response.url[response.url.index("=") + 1:len(response.url)]
            keyword = urllib.parse.unquote_plus(keyword)

        if "&page=" in response.url:
            page = int(response.url[response.url.index("&page=") + 6:len(response.url)])
        else:
            page = 1

        links = response.css("a.PartialSearchResults-item-title-link.result-link::attr(href)").getall()

        Sparql.is_endpoint(util.link_filter(links), Ask.name, keyword, page, first_crawl=Ask.is_first_crawl)

        next_page = response.css("li.PartialWebPagination-next a::attr(href)").get()

        if next_page is not None:
            yield Request(response.urljoin(next_page), callback=self.parse)

    def closed(self, reason):
        print(f"{self.name.upper()} is closed. ({reason})")
