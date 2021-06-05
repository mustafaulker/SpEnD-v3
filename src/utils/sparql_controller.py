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
        for link in links:
            # print(f"Current Website : {link}\n") # Debug print.
            # Site to be checked & Query & Timeout configuration
            sparql = SPARQLWrapper(link, returnFormat=JSON)
            sparql.setQuery("ASK WHERE { ?s ?p ?o. }")
            sparql.setTimeout(30)
            sparql.setOnlyConneg(True)
            link_domain = urlparse(link).netloc

            try:
                # Execute query and convert results to the returnFormat which is JSON.
                query_result = sparql.queryAndConvert()
                if query_result["boolean"] and not fe.db.in_the_collection("endpoints", link_domain):
                    fe.db.insert_endpoint(link, link_domain, spider_name, keyword, page)
                    # print(f"Endpoint written on DB. site : {link}\n") # Debug print.
                else:
                    if fe.db.in_the_collection("endpoints", link_domain):
                        if query_result["boolean"]:
                            fe.db.endpoint_alive_or_not(link, True)
                        # print(f"Endpoint already exist in DB. site : {link}\n") # Debug print.
                    else:
                        # print(f"This site isn't a SPARQL endpoint. site : {link}\n") # Debug print.
                        continue

            except (EndPointNotFound, EndPointInternalError, QueryBadFormed) as e:
                if first_crawl:  # first crawl
                    if is_alive(link) and not fe.db.in_the_collection("endpoints", link_domain) \
                            and not fe.db.in_the_collection("second_crawl_domains", link_domain):
                        fe.db.insert_crawl_domain(link_domain)
                        # print(f"This site's domain is added for second crawl. site : {link_domain}\n") # Debug print.
                    elif fe.db.in_the_collection("endpoints", link_domain) \
                            or fe.db.in_the_collection("second_crawl_domains", link_domain):
                        # print(f"This domain already exist in DB. site : {link_domain}\n") # Debug print.
                        continue
                    else:
                        # print(f"This site is not alive. site : {link}\n") # Debug print.
                        continue
                else:  # second crawl
                    continue

            except (HTTPError, URLError) as UrllibError:
                if first_crawl:  # first crawl
                    if "503" in str(UrllibError):
                        # print(f"This site is not alive. site : {link}\n") # Debug print.
                        continue
                    elif "certificate verify failed" in str(UrllibError) \
                            and not fe.db.in_the_collection("endpoints", link_domain) \
                            and not fe.db.in_the_collection("second_crawl_domains", link_domain):
                        fe.db.insert_crawl_domain(link_domain)
                        # print(f"This site's domain is added for second crawl. site : {link_domain}\n") # Debug print.
                    else:
                        Sparql.general_control_for_missed_endpoint(link, link_domain, spider_name, keyword, page)
                        # print("Urllib Error.\n") # Debug print.
                else:  # second crawl
                    Sparql.general_control_for_missed_endpoint_in_second_crawl(link, link_domain, spider_name, keyword,
                                                                               page)
                    continue

            except (SPARQLWrapperException, URITooLong, Unauthorized) as WrapperException:
                print(f"Error while wrapping endpoint: {WrapperException} site : {link}\n")
                # print("WrapperException\n") # Debug print.

            except TypeError:
                if first_crawl:  # first crawl
                    Sparql.general_control_for_missed_endpoint(link, link_domain, spider_name, keyword, page)
                    # print("Type Error\n") # Debug print.
                else:  # second crawl
                    Sparql.general_control_for_missed_endpoint_in_second_crawl(link, link_domain, spider_name, keyword,
                                                                               page)
                    continue

            except Exception:
                if first_crawl:  # first crawl
                    Sparql.general_control_for_missed_endpoint(link, link_domain, spider_name, keyword, page)
                    # print('Exception: \n') # Debug print.
                else:  # second crawl
                    Sparql.general_control_for_missed_endpoint_in_second_crawl(link, link_domain, spider_name, keyword,
                                                                               page)
                    continue

    @staticmethod
    def is_missed_endpoint(link: str) -> bool:
        missed = True
        path = urlparse(link).path
        domain = urlparse(link).netloc

        if not (path == "/sparql/" or path == "/sparql" or path.endswith("/sparql") or
                path.endswith("/sparql/") or domain.startswith("sparql.")):
            missed = False

        return missed

    @staticmethod
    def general_control_for_missed_endpoint(link: str, link_domain: str, spider_name: str, keyword: str, page: int):
        alive = is_alive(link)

        if alive:
            if Sparql.is_missed_endpoint(link) and not fe.db.in_the_collection("endpoints", link_domain) \
                    and not fe.db.in_the_collection("second_crawl_domains", link_domain):
                fe.db.insert_endpoint(link, link_domain, spider_name, keyword, page)
                # print(f"Endpoint written on DB. site : {link}\n") # Debug print.
            elif fe.db.in_the_collection("endpoints", link_domain) \
                    or fe.db.in_the_collection("second_crawl_domains", link_domain):
                # print(f"This domain already exist in DB. site : {link_domain}\n") # Debug print.
                pass
            else:
                fe.db.insert_crawl_domain(link_domain)
                # print(f"This site's domain is added for second crawl. site : {link_domain}\n") # Debug print.

    @staticmethod
    def general_control_for_missed_endpoint_in_second_crawl(link: str, link_domain: str, spider_name: str, keyword: str,
                                                            page: int):
        alive = is_alive(link)

        if alive:
            if Sparql.is_missed_endpoint(link) and not fe.db.in_the_collection("endpoints", link_domain):
                fe.db.insert_endpoint(link, link_domain, spider_name, keyword, page)
                # print(f"Endpoint written on DB. site : {link}\n") # Debug print.

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
