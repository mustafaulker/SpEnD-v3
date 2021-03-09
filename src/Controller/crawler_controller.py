from multiprocessing.pool import ThreadPool as Pool
from search_engines import *
from sys import stderr
from search_engines.engine import SearchEngine
from src.Util.link_filter import Filter
import time


class Crawler:

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
    def search_engine_crawler(keywords, search_engine: SearchEngine):
        """
        Crawls provided search_engine for every keyword.

        :param keywords: List of keywords to be searched
        :param search_engine: A search engine to be crawled
        """
        try:
            time.sleep(1)
            if isinstance(keywords, str):
                search_engine.search(keywords, pages=1)
            elif isinstance(keywords, list):
                for keyword in keywords:
                    search_engine.search(keyword, pages=1)
            else:
                raise ValueError("Invalid literal for \"keyword\" argument. \"keyword\" must be str or list.")
        except ValueError as valueError:
            stderr.write(str(valueError))
        except Exception as e:
            print('Error while performing search engine queries: ', e)

    @staticmethod
    def engines_to_pool(crawl_number: int, keywords, engine_list: list):
        """
        Gets search engine/engines as a parameter,
        in order to create a pool and execute "search_engine_crawler" func. async
        with provided search engines

        :param crawl_number: Determine which crawl is this. Transfers input to link_filter
        :param keywords: Keywords to be crawled on search engines
        :param engine_list: List of search engines to be allocated
        :return: Set of crawled links
        """
        try:
            pool = Pool(4)
            [pool.apply_async(Crawler.search_engine_crawler, (keywords, engine)) for engine in engine_list]
            pool.close()
            pool.join()
        except Exception as e:
            print('Error while performing processor pool allocating: ', e)

        crawling_results = []
        [crawling_results.extend(engine.results.links()) for engine in engine_list]
        print('Total link count after filtering: ', len(set(crawling_results)))

        Filter.triple_filtering(crawl_number, set(crawling_results))

    @staticmethod
    def single_search_engine(crawl_number: int, keywords, search_engine='google'):
        """
        Crawls web with user provided search engine.

        :param crawl_number: Determine which crawl is this. Transfers input to link_filter via engines_to_pool()
        :param keywords: Keywords to be crawled on search engines
        :param search_engine: Search engine name to be crawled.
        :return: crawl_results: Set of crawled websites.
        """
        return Crawler.engines_to_pool(crawl_number, keywords, [Crawler.engine_dict[search_engine]])

    @staticmethod
    def multiple_search_engine(crawl_number: int, keywords, *args):
        """
        Crawls web with user provided search engines.

        :param crawl_number: Determine which crawl is this. Transfers input to link_filter via engines_to_pool()
        :param keywords: Keywords to be crawled on search engines
        :param args: Names of search engines to be crawled. (Multiple arguments could be given.)
        :return: crawl_results: Set of crawled websites.
        """
        temp_engine_list = []
        [temp_engine_list.append(Crawler.engine_dict[engine]) for engine in args]

        return Crawler.engines_to_pool(crawl_number, keywords, temp_engine_list)

    @staticmethod
    def all_search_engines(crawl_number: int, keywords):
        """
        Crawls all the search engines defined in the engine_dict.
        :param crawl_number: Determine which crawl is this. Transfers input to link_filter via engines_to_pool()
        :param keywords: Keywords to be crawled on search engines
        :return: crawl_results: Set of crawled websites.
        """
        return Crawler.engines_to_pool(crawl_number, keywords, list(Crawler.engine_dict.values()))
