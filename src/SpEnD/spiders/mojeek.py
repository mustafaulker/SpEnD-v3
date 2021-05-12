import urllib.parse

import scrapy
from scrapy import Request

from src.utils import util
from src.utils.sparql_controller import Sparql


class Mojeek(scrapy.Spider):
    name = "mojeek"
    base_url = "https://www.mojeek.com/search?q="
    is_first_crawl = True

    custom_settings = {
        "CONCURRENT_REQUESTS": 4,
        "CONCURRENT_REQUESTS_PER_IP": 4,
        "DOWNLOAD_DELAY": 7,
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
