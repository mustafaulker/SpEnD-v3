import datetime
import urllib.parse
from sys import stderr

import requests
from urllib3.exceptions import *

from src.utils.database_controller import Database

Database.initialize()

default_unwanted_keys = Database.get_keywords("unwanted_keys")
default_wanted_keys = Database.get_keywords("wanted_keys")
default_second_crawl_keys = Database.get_keywords("second_crawl_keys")
second_crawl_domains = Database.get_second_crawl_domains()


def link_filter(incoming_links: list) -> list:
    filtered_links = list()
    for link in incoming_links:
        if "help" in urllib.parse.urlparse(link).query:
            link = link.replace(link[link.index("?help"):len(link)], "")

        if any(wanted_key in link.lower() for wanted_key in default_wanted_keys):
            if not any(unwanted_key in link.lower() for unwanted_key in default_unwanted_keys):
                filtered_links.append(link)
        else:
            continue
    return filtered_links


def link_regulator_for_google(incoming_links: list) -> list:
    regulated_links = list()
    for link in incoming_links:
        if "/url?q=" in link:
            if "%3F" and "%3D" in link:
                link = link.replace("%3F", "?").replace("%3D", "=")
            regulated_links.append(link[link.index("=") + 1:link.index("&")])
        else:
            continue
    return regulated_links


def fill_start_urls_list(spider, query):
    try:
        if isinstance(query, str):
            query = urllib.parse.quote_plus(query)
            if spider.name == "google":
                spider.start_urls.append(spider.base_url + query + "&num=50")
            else:
                spider.start_urls.append(spider.base_url + query)
        elif isinstance(query, list):
            for key in query:
                key = urllib.parse.quote_plus(key)
                if spider.name == "google":
                    spider.start_urls.append(spider.base_url + key + "&num=50")
                else:
                    spider.start_urls.append(spider.base_url + key)
        else:
            raise ValueError("Invalid literal for \"query\" argument. \"query\" must be str or list.")
    except ValueError as valueError:
        stderr.write(str(valueError))


def fill_start_urls_list_for_second_crawl(spider, query):
    try:
        date = datetime.datetime.utcnow() - datetime.timedelta(days=7)
        if isinstance(query, str):
            for domain in second_crawl_domains:
                if "last_crawl" in domain:
                    if domain["last_crawl"] < date:
                        add_element_for_second_crawl(spider, query, domain)
                        Database.update("second_crawl_domains", {"domain": domain["domain"]},
                                        {"$set": {"last_crawl": datetime.datetime.utcnow()}})
                    else:
                        continue
                else:
                    add_element_for_second_crawl(spider, query, domain)
                    Database.update("second_crawl_domains", {"domain": domain["domain"]},
                                    {"$set": {"last_crawl": datetime.datetime.utcnow()}})
        elif isinstance(query, list):
            for domain in second_crawl_domains:
                if "last_crawl" in domain:
                    if domain["last_crawl"] < date:
                        for key in query:
                            add_element_for_second_crawl(spider, key, domain)
                        Database.update("second_crawl_domains", {"domain": domain["domain"]},
                                        {"$set": {"last_crawl": datetime.datetime.utcnow()}})
                    else:
                        continue
                else:
                    for key in query:
                        add_element_for_second_crawl(spider, key, domain)
                    Database.update("second_crawl_domains", {"domain": domain["domain"]},
                                    {"$set": {"last_crawl": datetime.datetime.utcnow()}})
        else:
            raise ValueError("Invalid literal for \"query\" argument. \"query\" must be str or list.")
    except ValueError as valueError:
        stderr.write(str(valueError))


def add_element_for_second_crawl(spider, query, domain):
    query = urllib.parse.quote_plus(f"{query} site:{domain['domain']}")
    if spider.name == "google":
        spider.start_urls.append(spider.base_url + query + "&num=100")
    else:
        spider.start_urls.append(spider.base_url + query)


def clear_start_urls_list(spider):
    spider.start_urls.clear()


def is_alive(link: str) -> bool:
    alive = False
    try:
        response = requests.get(link, timeout=40).status_code
        if response == 200:
            alive = True
        else:
            print("This site is not alive. Therefore this site will not add to Second_Crawl_Domains collection.")
    except (TimeoutError, NewConnectionError, MaxRetryError, requests.ConnectionError, requests.ReadTimeout):
        print("This site is not alive. Therefore this site will not add to Second_Crawl_Domains collection.")
    return alive
