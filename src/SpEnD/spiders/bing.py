import urllib.parse

import scrapy
from scrapy import Request

from src.utils import util
from src.utils.sparql_controller import Sparql


class Bing(scrapy.Spider):
    name = "bing"
    base_url = "https://www.bing.com/search?q="
    search_parameters = "&form=QBLH&count=50"
    is_first_crawl = True

    custom_settings = {
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:77.0) Gecko/20100101 Firefox/77.0",
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

        if "&first=" in response.url:
            page = response.url[response.url.index("&first=") + 7: response.url.index("&FORM")]
            if len(page) == 2:
                page = int(page[0]) + 1
            elif len(page) == 3:
                page = int(page[0:2]) + 1
            elif len(page) == 4:
                page = int(page[0:3]) + 1
        else:
            page = 1

        links = response.css("div.b_title a.sh_favicon::attr(href)").getall()

        Sparql.is_endpoint(util.link_filter(links), Bing.name, keyword, page, first_crawl=Bing.is_first_crawl)

        next_page = response.css("a.sb_pagN.sb_pagN_bp.b_widePag.sb_bp::attr(href)").get()

        if next_page is not None:
            yield Request(response.urljoin(next_page), callback=self.parse)
