import logging
from urllib.error import *
from urllib.parse import urlparse

from SPARQLWrapper import SPARQLWrapper, JSON
from SPARQLWrapper.SPARQLExceptions import *
from urllib3.exceptions import *

import src.frontend as fe
from src.utils.util import is_alive

logging.getLogger("py.warnings").setLevel(logging.ERROR)


class Sparql:

    @staticmethod
    def is_endpoint(links: list, spider_name: str, keyword: str, page: int, first_crawl=True):
        """
        Sends an ASK query to the provided links to check whether they are endpoints or not.

        :param links: Links to be checked
        :param spider_name: Spider name that found the endpoint
        :param keyword: Keywords that found the endpoint
        :param page: Search engine page info that endpoint found on
        :param first_crawl: Is it first crawl
        :return: None
        """
        for link in links:
            # Query configurations
            sparql = SPARQLWrapper(link, returnFormat=JSON)
            sparql.setQuery("ASK WHERE { ?s ?p ?o. }")
            sparql.setTimeout(30)
            sparql.setOnlyConneg(True)
            link_domain = urlparse(link).netloc

            try:
                # Execute query and convert the result to JSON format.
                query_result = sparql.queryAndConvert()
                if query_result["boolean"] and not fe.db.in_the_collection("endpoints", link_domain):
                    fe.db.insert_endpoint(link, link_domain, spider_name, keyword, page)
                else:
                    if fe.db.in_the_collection("endpoints", link_domain):
                        if query_result["boolean"]:
                            fe.db.endpoint_alive_or_not(link, True)
                    else:
                        continue

            except (EndPointNotFound, EndPointInternalError, QueryBadFormed):
                if first_crawl:
                    if is_alive(link) and not fe.db.in_the_collection("endpoints", link_domain) \
                            and not fe.db.in_the_collection("inner_domains", link_domain):
                        fe.db.insert_crawl_domain(link_domain)
                    elif fe.db.in_the_collection("endpoints", link_domain) \
                            or fe.db.in_the_collection("inner_domains", link_domain):
                        continue
                    else:
                        continue
                else:  # inner crawl
                    continue

            except (HTTPError, URLError) as UrllibError:
                if first_crawl:
                    if "503" in str(UrllibError):
                        continue
                    elif "certificate verify failed" in str(UrllibError) \
                            and not fe.db.in_the_collection("endpoints", link_domain) \
                            and not fe.db.in_the_collection("inner_domains", link_domain):
                        fe.db.insert_crawl_domain(link_domain)
                    else:
                        Sparql.missed_control(link, link_domain, spider_name, keyword, page)
                else:  # inner crawl
                    Sparql.inner_missed_control(link, link_domain, spider_name, keyword, page)
                    continue

            except (SPARQLWrapperException, URITooLong, Unauthorized) as WrapperException:
                print(f"Error while wrapping endpoint: {WrapperException} site : {link}\n")

            except TypeError:
                if first_crawl:
                    Sparql.missed_control(link, link_domain, spider_name, keyword, page)
                else:  # inner crawl
                    Sparql.inner_missed_control(link, link_domain, spider_name, keyword, page)
                    continue

            except Exception:
                if first_crawl:
                    Sparql.missed_control(link, link_domain, spider_name, keyword, page)
                else:  # inner crawl
                    Sparql.inner_missed_control(link, link_domain, spider_name, keyword, page)
                    continue

    @staticmethod
    def is_missed_endpoint(link: str) -> bool:
        """
        Checks if the link is can be a missed endpoint.

        :param link: Link to be checked
        :return: Is endpoint missed or not
        """
        missed = True
        path = urlparse(link).path
        domain = urlparse(link).netloc

        if not (path == "/sparql/" or path == "/sparql" or path.endswith("/sparql") or
                path.endswith("/sparql/") or domain.startswith("sparql.")):
            missed = False

        return missed

    @staticmethod
    def missed_control(link: str, link_domain: str, spider_name: str, keyword: str, page: int):
        """
        Checks if any endpoint missed.

        :param link: Link to be checked
        :param link_domain: Domain of the link
        :param spider_name: Spider name that found the endpoint
        :param keyword: Keywords that found the endpoint
        :param page: Search engine page info that endpoint found on
        :return: None
        """
        alive = is_alive(link)

        if alive:
            if Sparql.is_missed_endpoint(link) and not fe.db.in_the_collection("endpoints", link_domain) \
                    and not fe.db.in_the_collection("inner_domains", link_domain):
                fe.db.insert_endpoint(link, link_domain, spider_name, keyword, page)
            elif fe.db.in_the_collection("endpoints", link_domain) \
                    or fe.db.in_the_collection("inner_domains", link_domain):
                pass
            else:
                fe.db.insert_crawl_domain(link_domain)

    @staticmethod
    def inner_missed_control(link: str, link_domain: str, spider_name: str, keyword: str, page: int):
        """
        Checks if any endpoint missed for inner_crawl.

        :param link: Link to be checked
        :param link_domain: Domain of the link
        :param spider_name: Spider name that found the endpoint
        :param keyword: Keywords that found the endpoint
        :param page: Search engine page info that endpoint found on
        :return: None
        """
        alive = is_alive(link)

        if alive:
            if Sparql.is_missed_endpoint(link) and not fe.db.in_the_collection("endpoints", link_domain):
                fe.db.insert_endpoint(link, link_domain, spider_name, keyword, page)

    @staticmethod
    def check_endpoints():
        """
        Gets all endpoints, checks if they are alive or not.
        According to the result, updates their status.

        :return: None
        """
        fe.logger.info('Status check has started.')
        for endpoint in fe.db.get_endpoints():
            if is_alive(endpoint):
                fe.db.endpoint_alive_or_not(endpoint, True)
            else:
                fe.db.endpoint_alive_or_not(endpoint, False)
        fe.logger.info('Status check has stopped.')
