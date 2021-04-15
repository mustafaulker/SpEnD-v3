import scrapy
from scrapy import Request
from src.utils import util
from src.utils.sparql_controller import Sparql


class Mojeek(scrapy.Spider):
    name = "mojeek"
    base_url = "https://www.mojeek.com/search?q="
    is_first_crawl = True

    start_urls = []

    def parse(self, response):

        links = response.css("a.ob::attr(href)").getall()

        Sparql.is_endpoint(util.link_filter(links), first_crawl=Mojeek.is_first_crawl)

        next_page = response.css("div.pagination a::attr(href)").getall()[-1]

        if next_page is not None:
            yield Request(response.urljoin(next_page), callback=self.parse)
