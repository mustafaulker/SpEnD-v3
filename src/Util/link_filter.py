from src.Controller.sparql_controller import Sparql
from src.Controller.database_controller import Database
from datetime import datetime
from urllib.parse import urlparse


class Filter:

    Database.initialize()

    # Default list to filtering wanted keywords in crawled links
    default_wanted_keys = Database.get_keywords("wanted_keys")

    # Default list to filtering unwanted keywords in crawled links
    default_unwanted_keys = Database.get_keywords("unwanted_keys")

    @staticmethod
    def filter_wanted_keywords(links, wanted_keys=default_wanted_keys):
        """
        Filter out wanted links in the search results.
        Rest of the links will not be checked for Endpoint.

        :param links: Search result links list.
        :param wanted_keys: Keywords to be applied as a filter to keep links that contains wanted keywords.
        :return: Filtered links set.
        """
        wanted_links = []
        for filter_word in wanted_keys:
            for link in links:
                if filter_word in link.lower():
                    wanted_links.append(link)
        return set(wanted_links)

    @staticmethod
    def filter_unwanted_keywords(links, unwanted_keys=default_unwanted_keys):
        """
        Filter out wanted links in the search results.
        Links which contains unwanted keywords, will be deleted from results.

        :param links: Search result links list.
        :param unwanted_keys: Keywords to be applied as a filter to remove links that contains unwanted keywords.
        :return: Filtered links set.
        """
        unwanted_links = []
        for filter_word in unwanted_keys:
            for link in links:
                if filter_word in link.lower():
                    unwanted_links.append(link)
        return set(links) - set(unwanted_links)

    @staticmethod
    def filter_suffix(links, suffix='?help'):
        """
        Filter out unwanted suffixes in the search results.

        :param links: Search result links list.
        :param suffix: Link suffixes to be deleted.
        :return: Filtered links set
        """
        arranged_link, to_remove = [], []
        for link in links:
            if suffix in link.lower():
                to_remove.append(link)
                arranged_link.append(link.split(suffix)[0])

        return set(list(links) + arranged_link) - set(to_remove)

    @staticmethod
    def triple_filtering(crawl_number, links, wanted_keys=default_wanted_keys,
                         unwanted_keys=default_unwanted_keys, suffix='?help'):
        """
        Method to use wanted/unwanted/suffix methods at once.

        :param crawl_number: Determine which crawl is this. Changes function based on the input.
        :param links: Search result links list.
        :param wanted_keys: Keywords to be applied as a filter to keep links that contains wanted keywords.
        :param unwanted_keys: Keywords to be applied as a filter to remove links that contains unwanted keywords.
        :param suffix: Link suffixes to be deleted.
        :return: Filtered search result links.
        """
        filtered_links = Filter.filter_suffix(
            Filter.filter_unwanted_keywords(
                Filter.filter_wanted_keywords(links, wanted_keys), unwanted_keys), suffix)

        for link in filtered_links:
            domain = urlparse(link).netloc
            if not Database.find_one('Domains', {"domain": domain}):
                Database.insert_one('Domains',
                                    {'date_created': datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                                     'domain': domain})
        if crawl_number == 1:
            Sparql.endpoints_to_pool(filtered_links)
        elif crawl_number == 2:
            for link in filtered_links:
                if not Database.find_one('ReCrawl_Links', {"rc_url": link}):
                    Database.insert_one('ReCrawl_Links',
                                        {'date_created': datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                                         'rc_url': link})
