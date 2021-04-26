import scrapy
from scrapy import Request

from src.utils import util
from src.utils.sparql_controller import Sparql


class Google(scrapy.Spider):
    name = "google"
    base_url = "https://www.google.com/search?q="
    is_first_crawl = True

    custom_settings = {
        "CONCURRENT_REQUESTS": 1,
        "CONCURRENT_REQUESTS_PER_IP": 1,
        "DOWNLOAD_DELAY": 40,
    }

    start_urls = []

    def parse(self, response):

        links = response.css("div.kCrYT a::attr(href)").getall()

        Sparql.is_endpoint(util.link_filter(util.link_regulator_for_google(links)), first_crawl=Google.is_first_crawl)

        next_page = response.css("a.nBDE1b.G5eFlf::attr(href)").get()

        if "&start=50" in response.url:
            if len(response.css("a.nBDE1b.G5eFlf::attr(href)").getall()) == 1:
                next_page = None
            else:
                next_page = response.css("a.nBDE1b.G5eFlf::attr(href)").getall()[1]

        if next_page is not None:
            yield Request(response.urljoin(next_page), callback=self.parse)
