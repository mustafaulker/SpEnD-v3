from multiprocessing.pool import ThreadPool as Pool
from search_engines import *


class Crawler:

    # Default keyword list
    default_query_list = ['sparql query', '"sparql endpoint"', 'inurl:sparql',
                          'allintitle: sparql query', 'allinurl: sparql data']

    # All search engines
    engine_dict = {
        'google_engine': Google(),
        'bing_engine': Bing(),
        'yahoo_engine': Yahoo(),
        'duckduckgo_engine': Duckduckgo(),
        'ask_engine': Ask(),
        'aol_engine': Aol(),
        'mojeek_engine': Mojeek(),
        'dogpile_engine': Dogpile()
    }

    @staticmethod
    def search_engine_crawler(search_engine, keywords=default_query_list):
        """
        Crawls provided search_engine for every keyword.

        :param search_engine: A search engine to be crawled
        :param keywords: List of keywords to be searched
        """
        for keyword in keywords:
            try:
                search_engine.search(keyword)
            except Exception as e:
                print('Error while performing search engine queries. - ', e)

    @staticmethod
    def engines_to_pool(engine_list):
        """
        Gets search engine/engines as a parameter,
        in order to create a pool and execute "search_engine_crawler" func. async
        with provided search engines

        :param engine_list: List of search engines to be allocated
        :return: a Set of crawled links
        """
        try:
            pool = Pool(4)
            for engine in engine_list:
                pool.apply_async(Crawler.search_engine_crawler, (engine,))
            pool.close()
            pool.join()
        except Exception as e:
            print('Error while performing processor pool allocating. - ', e)

        crawl_results = []
        for engine in Crawler.engine_dict.values():
            if not (not engine.results.links()):    # if links() list is not empty
                crawl_results.extend(engine.results.links())
        return set(crawl_results)

    @staticmethod
    def single_search_engine(search_engine='google_engine'):
        """
        Crawls web with user provided search engine.

        :param search_engine: Search engine name to be crawled.
        :return: crawl_results: Set of crawled websites.
        """
        temp_engine_list = [Crawler.engine_dict[search_engine]]
        return Crawler.engines_to_pool(temp_engine_list)

    @staticmethod
    def multiple_search_engine(*args):
        """
        Crawls web with user provided search engines.

        :param args: Names of search engines to be crawled. (Multiple arguments could be given.)
        :return: crawl_results: Set of crawled websites.
        """
        temp_engine_list = []
        for engine in args:
            temp_engine_list.append(Crawler.engine_dict[engine])

        return Crawler.engines_to_pool(temp_engine_list)

    @staticmethod
    def all_search_engines():
        """
        Crawls all the search engines defined in the engine_dict.

        :return: crawl_results: Set of crawled websites.
        """
        return Crawler.engines_to_pool(list(Crawler.engine_dict.values()))
