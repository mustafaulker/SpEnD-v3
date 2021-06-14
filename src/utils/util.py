import datetime
import logging
import urllib.parse
from sys import stderr

import requests
from urllib3.exceptions import *

import src.frontend as fe

unwanted_keys = fe.db.get_keywords("unwanted_keys")
wanted_keys = fe.db.get_keywords("wanted_keys")
inner_keys = fe.db.get_keywords("inner_keys")
inner_domains = fe.db.get_inner_domains()


def link_filter(incoming_links: list) -> list:
    """
    Filters the provided links based on wanted & unwanted keys.

    Firstly checks the query part of incoming links. If there is "?help" part in the query section,
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

        if any(wanted_key in link.lower() for wanted_key in wanted_keys):
            if not any(unwanted_key in link.lower() for unwanted_key in unwanted_keys):
                filtered_links.append(link)
        else:
            continue
    return filtered_links


def link_regulator(incoming_links: list) -> list:
    """
    Regulates the links coming from Google Search.

    Input URL: "/url?q=https://www.example.com/SparqlEndpoint&sa=U&ved=2ahUKEwiU"

    Output URL: "https://www.example.com/SparqlEndpoint"

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


def fill_urls(spider, query):
    """
    Fills the start_urls list for the specified spider.

    Parses the query keyword for the search engine. Inserts parsed keyword into the specified spider's start_urls list.

    :param spider: Spider which start_urls list to be filled
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


def fill_inner_urls(spider, query):
    """
    Fills the start_urls list of the specified spider for inner crawl.

    Parses the query keyword for the search engine. Inserts parsed keyword into the specified spider's start_urls list.

    :param spider: Spider which start_urls list to be filled
    :param query: Keyword list or keyword string for the search query
    :return: None
    """
    try:
        date = datetime.datetime.utcnow() - datetime.timedelta(days=7)
        if isinstance(query, str):
            for domain in inner_domains:
                if "last_crawl" in domain:
                    if domain["last_crawl"] < date:
                        add_inner_element(spider, query, domain)
                        fe.db.update_one("inner_domains", {"domain": domain["domain"]},
                                         {"$set": {"last_crawl": datetime.datetime.utcnow()}})
                    else:
                        continue
                else:
                    add_inner_element(spider, query, domain)
                    fe.db.update_one("inner_domains", {"domain": domain["domain"]},
                                     {"$set": {"last_crawl": datetime.datetime.utcnow()}})
        elif isinstance(query, tuple):
            for domain in inner_domains:
                if "last_crawl" in domain:
                    if domain["last_crawl"] < date:
                        for key in query:
                            add_inner_element(spider, key, domain)
                        fe.db.update_one("inner_domains", {"domain": domain["domain"]},
                                         {"$set": {"last_crawl": datetime.datetime.utcnow()}})
                    else:
                        continue
                else:
                    for key in query:
                        add_inner_element(spider, key, domain)
                    fe.db.update_one("inner_domains", {"domain": domain["domain"]},
                                     {"$set": {"last_crawl": datetime.datetime.utcnow()}})
        else:
            raise ValueError("Invalid literal for \"query\" argument. \"query\" must be str or tuple.")
    except ValueError as valueError:
        stderr.write(str(valueError))


def add_inner_element(spider, query, domain):
    """
    Inserts domain to specified spider's start_urls list for inner crawl.

    Parses the query keyword for the search engine. Inserts parsed keyword into the specified spider's start_urls list.

    :param spider: Spider which start_urls list to be filled
    :param query: Keyword string for the search query
    :param domain: Domain to be inserted
    :return: None
    """
    query = urllib.parse.quote_plus(f"{query} site:{domain['domain']}")
    spider.start_urls.append(spider.base_url + query + spider.search_parameters)


def clear_urls(spider):
    """
    Clears the start_urls list for the specified spider.

    :param spider: Spider which start_urls list to be cleaned
    :return: None
    """
    spider.start_urls.clear()


def is_alive(link: str) -> bool:
    """
    Checks whether specified site is alive or not.

    :param link: Link of the site to be checked
    :return: Boolean based on the site's response
    """
    logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)
    alive = False
    try:
        response = requests.get(link, timeout=40).status_code
        if response == 200:
            alive = True
        else:
            pass
    except (TimeoutError, NewConnectionError, MaxRetryError, requests.ConnectionError, requests.ReadTimeout):
        pass
    return alive
