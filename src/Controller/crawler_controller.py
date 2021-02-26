from multiprocessing.pool import ThreadPool as Pool
from search_engines import *


class Crawler:

    # Default keyword to execute queries
    default_keyword_list = ['sparql query', '"sparql endpoint"', 'inurl:sparql',
                            'allintitle: sparql query', 'allinurl: sparql data']

    # All search engines
    engine_dict = {
        'google': Google(),
        'bing': Bing(),
        'yahoo': Yahoo(),
        'duckduckgo': Duckduckgo(),
        'ask': Ask(),
        'aol': Aol(),
        'mojeek': Mojeek(),
        'dogpile': Dogpile()
    }

    @staticmethod
    def search_engine_crawler(search_engine, keywords=default_keyword_list):
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
        :return: Set of crawled links
        """
        try:
            pool = Pool(4)
            [pool.apply_async(Crawler.search_engine_crawler, (engine,)) for engine in engine_list]
            pool.close()
            pool.join()
        except Exception as e:
            print('Error while performing processor pool allocating: ', e)

        crawling_results = []
        [crawling_results.extend(engine.results.links()) for engine in engine_list]
        print('Total link count after filtering: ', len(set(crawling_results)))

        return set(crawling_results)

    @staticmethod
    def single_search_engine(search_engine='google'):
        """
        Crawls web with user provided search engine.

        :param search_engine: Search engine name to be crawled.
        :return: crawl_results: Set of crawled websites.
        """
        return Crawler.engines_to_pool([Crawler.engine_dict[search_engine]])

    @staticmethod
    def multiple_search_engine(*args):
        """
        Crawls web with user provided search engines.

        :param args: Names of search engines to be crawled. (Multiple arguments could be given.)
        :return: crawl_results: Set of crawled websites.
        """
        temp_engine_list = []
        [temp_engine_list.append(Crawler.engine_dict[engine]) for engine in args]

        return Crawler.engines_to_pool(temp_engine_list)

    @staticmethod
    def all_search_engines():
        """
        Crawls all the search engines defined in the engine_dict.

        :return: crawl_results: Set of crawled websites.
        """
        return Crawler.engines_to_pool(list(Crawler.engine_dict.values()))
