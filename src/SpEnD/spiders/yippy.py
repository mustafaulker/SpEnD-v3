import scrapy
from scrapy import Request
from src.utils import util
from src.utils.sparql_controller import Sparql


class Yippy(scrapy.Spider):
    name = "yippy"
    base_url = "https://yippy.com/search?query="
    is_first_crawl = True

    start_urls = []

    def parse(self, response):
        links = response.css("a.title::attr(href)").getall()

        Sparql.is_endpoint(util.link_filter(links), first_crawl=Yippy.is_first_crawl)

        next_page = response.css("a.listnext::attr(href)").get()

        if next_page is not None:
            yield Request(response.urljoin(next_page), callback=self.parse)
