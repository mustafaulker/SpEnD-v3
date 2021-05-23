import urllib.parse

import scrapy
from scrapy import Request

from src.utils import util
from src.utils.sparql_controller import Sparql


class Aol(scrapy.Spider):
    name = "aol"
    base_url = "https://search.aol.com/aol/search?q="
    search_parameters = ""
    is_first_crawl = True

    start_urls = []

    def parse(self, response):
        keyword = response.url[response.url.index("=") + 1:response.url.index("&")]
        keyword = urllib.parse.unquote_plus(keyword)

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

        links = response.css("a.ac-algo.fz-l.ac-21th.lh-24::attr(href)").getall()

        Sparql.is_endpoint(util.link_filter(links), Aol.name, keyword, page, first_crawl=Aol.is_first_crawl)

        next_page = response.css("a.next::attr(href)").get()

        if next_page is not None:
            yield Request(response.urljoin(next_page), callback=self.parse)
