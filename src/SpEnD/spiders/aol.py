import scrapy
from scrapy import Request
from src.utils import util
from src.utils.sparql_controller import Sparql


class Aol(scrapy.Spider):
    name = "aol"
    base_url = "https://search.aol.com/aol/search?q="
    is_first_crawl = True

    start_urls = []

    def parse(self, response):

        links = response.css("a.ac-algo.fz-l.ac-21th.lh-24::attr(href)").getall()

        Sparql.is_endpoint(util.link_filter(links), first_crawl=Aol.is_first_crawl)

        next_page = response.css("a.next::attr(href)").get()

        if next_page is not None:
            yield Request(response.urljoin(next_page), callback=self.parse)
