import scrapy
from scrapy import Request

from src.utils import util
from src.utils.sparql_controller import Sparql


class Bing(scrapy.Spider):
    name = "bing"
    base_url = "https://www.bing.com/search?q="
    is_first_crawl = True

    start_urls = []

    def parse(self, response):
        links = response.css("div.b_title a.sh_favicon::attr(href)").getall()

        Sparql.is_endpoint(util.link_filter(links), first_crawl=Bing.is_first_crawl)

        next_page = response.css("a.sb_pagN.sb_pagN_bp.b_widePag.sb_bp::attr(href)").get()

        if next_page is not None:
            yield Request(response.urljoin(next_page), callback=self.parse)
