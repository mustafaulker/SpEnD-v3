from urllib.error import *
from urllib.parse import urlparse

from SPARQLWrapper import SPARQLWrapper, JSON
from SPARQLWrapper.SPARQLExceptions import *
from urllib3.exceptions import *

from src.utils.database_controller import Database
from src.utils.util import is_alive


class Sparql:

    @staticmethod
    def is_endpoint(links: list, spider_name: str, keyword: str, page: int, first_crawl=True):
        for link in links:
            print(f"\nCurrent Website : {link}")
            # Site to be checked & Query & Timeout configuration
            sparql = SPARQLWrapper(link, returnFormat=JSON)
            sparql.setQuery("ASK WHERE { ?s ?p ?o. }")
            sparql.setTimeout(30)
            sparql.setOnlyConneg(True)
            link_domain = urlparse(link).netloc

            try:
                # Execute query and convert results to the returnFormat which is JSON.
                query_result = sparql.queryAndConvert()
                if query_result["boolean"] and not Database.in_the_collection("endpoints", link_domain):
                    Database.insert_endpoint(link, link_domain, spider_name, keyword, page)
                    print("Endpoint written on DB.")
                else:
                    if Database.in_the_collection("endpoints", link_domain):
                        if query_result["boolean"]:
                            Database.endpoint_alive_or_not(link, True)
                        print("Endpoint already exist in DB.")
                    else:
                        print("This site isn't a SPARQL endpoint.")

            except (EndPointNotFound, EndPointInternalError, QueryBadFormed) as e:
                if first_crawl:  # first crawl
                    if is_alive(link) and not Database.in_the_collection("endpoints", link_domain) \
                            and not Database.in_the_collection("second_crawl_domains", link_domain):
                        Database.insert_crawl_domain(link_domain)
                        print(f"This site's domain is added for second crawl. site : {link_domain}")
                    elif Database.in_the_collection("endpoints", link_domain) \
                            or Database.in_the_collection("second_crawl_domains", link_domain):
                        print("This domain already exist in DB.")
                    else:
                        print("This site is not alive.")
                        continue
                else:  # second crawl
                    continue

            except (HTTPError, URLError) as UrllibError:
                if first_crawl:  # first crawl
                    if "503" in str(UrllibError):
                        print("This site is not alive.")
                    elif "certificate verify failed" in str(UrllibError) \
                            and not Database.in_the_collection("endpoints", link_domain) \
                            and not Database.in_the_collection("second_crawl_domains", link_domain):
                        Database.insert_crawl_domain(link_domain)
                        print(f"This site's domain is added for second crawl. site : {link_domain}")
                    else:
                        Sparql.general_control_for_missed_endpoint(link, link_domain, spider_name, keyword, page)
                        print("Urllib Error.")
                else:  # second crawl
                    Sparql.general_control_for_missed_endpoint_in_second_crawl(link, link_domain, spider_name, keyword,
                                                                               page)
                    continue

            except (SPARQLWrapperException, URITooLong, Unauthorized) as WrapperException:
                print("Error while wrapping endpoint: ", WrapperException)
                print("WrapperException")

            except TypeError:
                if first_crawl:  # first crawl
                    Sparql.general_control_for_missed_endpoint(link, link_domain, spider_name, keyword, page)
                    print("Type Error")
                else:  # second crawl
                    Sparql.general_control_for_missed_endpoint_in_second_crawl(link, link_domain, spider_name, keyword,
                                                                               page)
                    continue

            except Exception:
                if first_crawl:  # first crawl
                    Sparql.general_control_for_missed_endpoint(link, link_domain, spider_name, keyword, page)
                    print('Exception: ')
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
            if Sparql.is_missed_endpoint(link) and not Database.in_the_collection("endpoints", link_domain) \
                    and not Database.in_the_collection("second_crawl_domains", link_domain):
                Database.insert_endpoint(link, link_domain, spider_name, keyword, page)
                print("Endpoint written on DB.")
            elif Database.in_the_collection("endpoints", link_domain) \
                    or Database.in_the_collection("second_crawl_domains", link_domain):
                print("This domain already exist in DB.")
            else:
                Database.insert_crawl_domain(link_domain)
                print(f"This site's domain is added for second crawl. site : {link_domain}")

    @staticmethod
    def general_control_for_missed_endpoint_in_second_crawl(link: str, link_domain: str, spider_name: str, keyword: str,
                                                            page: int):
        alive = is_alive(link)

        if alive:
            if Sparql.is_missed_endpoint(link) and not Database.in_the_collection("endpoints", link_domain):
                Database.insert_endpoint(link, link_domain, spider_name, keyword, page)
                print("Endpoint written on DB.")

    @staticmethod
    def check_endpoints():
        """
        Gets all endpoints, checks if they are alive or not.
        According to the result, updates their status.

        :return: None
        """
        for endpoint in Database.get_endpoints():
            if is_alive(endpoint):
                Database.endpoint_alive_or_not(endpoint, True)
            else:
                Database.endpoint_alive_or_not(endpoint, False)
