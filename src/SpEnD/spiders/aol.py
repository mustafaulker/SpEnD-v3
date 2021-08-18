import logging
import urllib.parse

import scrapy
from scrapy import Request

from src.utils import util
from src.utils.sparql_controller import Sparql


class Aol(scrapy.Spider):

    def __init__(self, *args, **kwargs):
        logging.getLogger("scrapy.downloadermiddlewares.redirect").setLevel(logging.INFO)
        logging.getLogger("scrapy.middleware").setLevel(logging.WARNING)
        logging.getLogger("scrapy.extensions").setLevel(logging.WARNING)
        logging.getLogger("scrapy.statscollectors").setLevel(logging.WARNING)
        logging.getLogger("scrapy.crawler").setLevel(logging.WARNING)
        super().__init__(*args, **kwargs)

    name = "aol"
    base_url = "https://search.aol.com/aol/search?q="
    search_parameters = ""
    is_first_crawl = True

    custom_settings = {
        "USER_AGENT": "",
        "CONCURRENT_REQUESTS": 1,
        "CONCURRENT_REQUESTS_PER_IP": 1,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
        "DOWNLOAD_DELAY": 7,
        "COOKIES_ENABLED": False
    }

    start_urls = []

    def parse(self, response):
        # Extracting query keyword from the response URL.
        keyword = response.url[response.url.index("=") + 1:response.url.index("&")]
        keyword = urllib.parse.unquote_plus(keyword)

        # Extracting page number from the response URL.
        if "&b=" in response.url:
            page = response.url[response.url.index("&b=") + 3: response.url.index("&pz=10&bct")]
            if len(page) == 2:
                page = int(page[0]) + 1
            elif len(page) == 3:
                page = int(page[0:2]) + 1
            elif len(page) == 4:
                page = int(page[0:3]) + 1
        else:
            page = 1

        # Extracting all links from the response URL.
        links = response.css("a.ac-algo.fz-l.ac-21th.lh-24::attr(href)").getall()

        # Checking the links whether they are endpoints or not.
        Sparql.is_endpoint(util.link_filter(links), Aol.name, keyword, page, first_crawl=Aol.is_first_crawl)

        # Extracting next page URL from the response URL.
        next_page = response.css("a.next::attr(href)").get()

        if next_page is not None:
            yield Request(response.urljoin(next_page), callback=self.parse)

    def closed(self, reason):
        logging.getLogger("scrapy.core.engine").info(f"{self.name.upper()} is closed. ({reason})")
