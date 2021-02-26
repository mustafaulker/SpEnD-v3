from datetime import datetime
from multiprocessing.pool import ThreadPool as Pool
from SPARQLWrapper import SPARQLWrapper, JSON
from SPARQLWrapper.SPARQLExceptions import *
from urllib.error import *
from src.Controller.database_controller import Database


class Sparql:

    @staticmethod
    def is_endpoint(crawl_result):
        """
        Checks if given crawl_results are SparQL Endpoint or not,
        if so inserts them to Database.

        :param crawl_result: List of crawled websites
        """
        for link in crawl_result:
            print("\nCurrent website: " + link)
            # Site to be checked & Query & Timeout configuration
            sparql = SPARQLWrapper(f'{link}', returnFormat=JSON)
            sparql.setQuery("ASK WHERE { ?s ?p ?o. }")
            sparql.setTimeout(30)
            sparql.setOnlyConneg(True)
            try:
                # Execute query and convert results to the returnFormat which is JSON.
                query_result = sparql.queryAndConvert()
                if query_result['boolean']:  # if query_result['boolean'] is True, this website is an Endpoint.

                    # Database insertion with Current Date & Query site's URL & Endpoint
                    Database.insert_one('Endpoints', {'date_created': datetime.utcnow(),
                                                      'url': link,
                                                      'endpoint': query_result})
                    print('Endpoint found & Successfully written to DB.')
                else:
                    print("This site isn't a SparQL Endpoint.")
            except (HTTPError, URLError) as UrllibError:
                print('Urllib Error: ', UrllibError)
            except (EndPointInternalError, EndPointNotFound, SPARQLWrapperException,
                    QueryBadFormed, URITooLong, Unauthorized) as WrapperException:
                print("Error while wrapping endpoint: ", WrapperException)
            except Exception:
                print('Exception: ')

    @staticmethod  # (Possible +1 small piece due to fractional structure)
    def endpoints_to_pool(links):
        """
        Slices crawled links to four equal pieces in order to process simultaneously.

        :param links: List of crawled websites.
        """
        pieced_lists = [list(links)[i:i + (len(links) // 4)] for i in range(0, len(links), (len(links) // 4))]
        try:
            pool = Pool(4)
            [pool.apply_async(Sparql.is_endpoint, (list_piece,)) for list_piece in pieced_lists]
            pool.close()
            pool.join()
        except Exception as e:
            print('Error while performing processor pool allocating: ', e)
