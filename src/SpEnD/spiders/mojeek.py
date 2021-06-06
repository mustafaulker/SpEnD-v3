import logging
import urllib.parse

import scrapy
from scrapy import Request

from src.utils import util
from src.utils.sparql_controller import Sparql


class Mojeek(scrapy.Spider):

    def __init__(self, *args, **kwargs):
        logging.getLogger("scrapy.downloadermiddlewares.redirect").setLevel(logging.INFO)
        logging.getLogger("scrapy.middleware").setLevel(logging.WARNING)
        logging.getLogger("scrapy.extensions").setLevel(logging.WARNING)
        logging.getLogger("scrapy.statscollectors").setLevel(logging.WARNING)
        logging.getLogger("scrapy.crawler").setLevel(logging.WARNING)
        super().__init__(*args, **kwargs)

    name = "mojeek"
    base_url = "https://www.mojeek.com/search?q="
    search_parameters = "&t=40"
    is_first_crawl = True

    custom_settings = {
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
        "CONCURRENT_REQUESTS": 1,
        "CONCURRENT_REQUESTS_PER_IP": 1,
        "DOWNLOAD_DELAY": 10,
    }

    start_urls = []
    handle_httpstatus_list = [403]

    def parse(self, response):
        if "&" in response.url:
            keyword = response.url[response.url.index("=") + 1:response.url.index("&")]
            keyword = urllib.parse.unquote_plus(keyword)
        else:
            keyword = response.url[response.url.index("=") + 1:len(response.url)]
            keyword = urllib.parse.unquote_plus(keyword)

        if "&s=" in response.url:
            page = response.url[response.url.index("s=") + 2:len(response.url)]
            if len(page) == 2:
                page = int(page[0]) + 1
            elif len(page) == 3:
                page = int(page[0:2]) + 1
            elif len(page) == 4:
                page = int(page[0:3]) + 1
        else:
            page = 1

        links = response.css("a.ob::attr(href)").getall()

        Sparql.is_endpoint(util.link_filter(links), Mojeek.name, keyword, page, first_crawl=Mojeek.is_first_crawl)

        if not response.css("div.pagination a::attr(href)").getall():
            next_page = None
        else:
            next_page = response.css("div.pagination a::attr(href)").getall()[-1]

        if next_page is not None:
            yield Request(response.urljoin(next_page), callback=self.parse)

    def closed(self, reason):
        print(f"{self.name.upper()} is closed. ({reason})")
