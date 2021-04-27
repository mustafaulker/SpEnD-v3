import scrapy
from scrapy import Request

from src.utils import util
from src.utils.sparql_controller import Sparql


class Ask(scrapy.Spider):
    name = "ask"
    base_url = "https://www.ask.com/web?q="
    is_first_crawl = True

    start_urls = []

    def parse(self, response):
        links = response.css("a.PartialSearchResults-item-title-link.result-link::attr(href)").getall()

        Sparql.is_endpoint(util.link_filter(links), first_crawl=Ask.is_first_crawl)

        next_page = response.css("li.PartialWebPagination-next a::attr(href)").get()

        if next_page is not None:
            yield Request(response.urljoin(next_page), callback=self.parse)
