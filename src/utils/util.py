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
    """
    This method firstly checks the query part of incoming links. If there is "?help" part in the query section,
    this part will be deleted from "?" index to end of the query part. Then, it checks the presence of the "wanted"
    and "unwanted" keys in the link. If there is no "wanted" key in the incoming link, link will be eliminated.
    If one of the "wanted" keys exist and there is no "unwanted" key in the link, then link will be added to
    filtered links list.

    :param incoming_links: List of links to be filtered
    :return: List of filtered links
    """

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
    """
    This method regulates the links coming from Google Search.

    Regulates the link structure from this structure :

    "/url?q=https://www.example.com/SparqlEndpoint&sa=U&ved=2ahUKEwiU"

    to this structure :

    "https://www.example.com/SparqlEndpoint"

    :param incoming_links: List of links to be regulated
    :return: List of regulated links
    """

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
    """
    This method fills the start_urls list of the specified spider.
    Firstly, the query keyword is parsed for the search engine.
    Then the parsed keyword is inserted into the specified spider's start_urls list.

    :param spider: Spider which start_urls list will be filled
    :param query: Keyword list or keyword string for the search query
    :return: None
    """

    try:
        if isinstance(query, str):
            query = urllib.parse.quote_plus(query)
            spider.start_urls.append(spider.base_url + query + spider.search_parameters)
        elif isinstance(query, list) or isinstance(query, tuple):
            for key in query:
                key = urllib.parse.quote_plus(key)
                spider.start_urls.append(spider.base_url + key + spider.search_parameters)
        else:
            raise ValueError("Invalid literal for \"query\" argument. \"query\" must be str, list or tuple.")
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
        elif isinstance(query, tuple):
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
            raise ValueError("Invalid literal for \"query\" argument. \"query\" must be str or tuple.")
    except ValueError as valueError:
        stderr.write(str(valueError))


def add_element_for_second_crawl(spider, query, domain):
    """
    This method inserts link domain to spider's start_urls list for second crawl.
    Firstly, the query keyword is parsed for the search engine.
    Then the parsed keyword is inserted into the specified spider's start_urls list.

    :param spider: Spider which start_urls list will be filled
    :param query: Keyword string for the search query
    :param domain: JSON Object from second_crawl_domains collection
    :return: None
    """

    query = urllib.parse.quote_plus(f"{query} site:{domain['domain']}")
    spider.start_urls.append(spider.base_url + query + spider.search_parameters)


def clear_start_urls_list(spider):
    """
    This method clears the spider's start_urls list.

    :param spider: Spider which start_urls list will be cleaned
    :return: None
    """

    spider.start_urls.clear()


def is_alive(link: str) -> bool:
    """
    This method checks whether site is alive or not.

    :param link: Link of the site to be checked whether it is live or not
    :return: Boolean based response according to site's response
    """

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
