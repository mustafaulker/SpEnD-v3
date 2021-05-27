import logging
import urllib.parse

import scrapy
from scrapy import Request

from src.utils import util
from src.utils.sparql_controller import Sparql


class Google(scrapy.Spider):

    def __init__(self, *args, **kwargs):
        logging.getLogger("scrapy.downloadermiddlewares.redirect").setLevel(logging.INFO)
        logging.getLogger("scrapy.middleware").setLevel(logging.WARNING)
        logging.getLogger("scrapy.extensions").setLevel(logging.WARNING)
        logging.getLogger("scrapy.statscollectors").setLevel(logging.WARNING)
        super().__init__(*args, **kwargs)

    name = "google"
    base_url = "https://www.google.com/search?q="
    search_parameters = "&num=100"
    is_first_crawl = True

    custom_settings = {
        "CONCURRENT_REQUESTS": 1,
        "CONCURRENT_REQUESTS_PER_IP": 1,
        "DOWNLOAD_DELAY": 40,
    }

    start_urls = []

    def parse(self, response):
        keyword = response.url[response.url.index("=") + 1:response.url.index("&")]
        keyword = urllib.parse.unquote_plus(keyword)

        if "&start=" in response.url:
            page = response.url[response.url.index("start=") + 6:response.url.index("&sa")]
            if len(page) == 3:
                page = int(page[0]) + 1
            elif len(page) == 4:
                page = int(page[0:2]) + 1
            elif len(page) == 5:
                page = int(page[0:3]) + 1
        else:
            page = 1

        links = response.css("div.kCrYT a::attr(href)").getall()

        Sparql.is_endpoint(util.link_filter(util.link_regulator_for_google(links)), Google.name, keyword, page,
                           first_crawl=Google.is_first_crawl)

        next_page = response.css("a.nBDE1b.G5eFlf::attr(href)").get()

        if "&start=100" in response.url:
            if len(response.css("a.nBDE1b.G5eFlf::attr(href)").getall()) == 1:
                next_page = None
            else:
                next_page = response.css("a.nBDE1b.G5eFlf::attr(href)").getall()[1]

        if next_page is not None:
            yield Request(response.urljoin(next_page), callback=self.parse)

    def closed(self, reason):
        print(f"{self.name.upper()} is closed. ({reason})")
