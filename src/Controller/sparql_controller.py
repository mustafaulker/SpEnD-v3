from datetime import datetime
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

        :param crawl_result: A list of crawled websites
        """
        for link in crawl_result:
            print("\nCurrent website: " + link)
            # Site to be checked & Query & Timeout configuration
            sparql = SPARQLWrapper(f'{link}', returnFormat=JSON)
            sparql.setQuery("ASK WHERE { ?s ?p ?o. }")
            sparql.setTimeout(15)
            try:
                # Make query and convert results to the returnFormat which is JSON.
                query_result = sparql.queryAndConvert()
                # if query_result['boolean'] is True, this website is an Endpoint.
                if query_result['boolean']:
                    # Database insertion with Current Date & Query site's URL & Endpoint
                    Database.insert_one('Endpoints', {'date_created': datetime.utcnow(),
                                                      'url': link,
                                                      'endpoint': query_result})
                    print('Successfully written to DB.')
                else:
                    print("This site isn't a SparQL Endpoint.")
            except (HTTPError, URLError) as UrllibError:
                print('Urllib Error: ', UrllibError)
            except (EndPointInternalError, EndPointNotFound, SPARQLWrapperException,
                    QueryBadFormed, URITooLong, Unauthorized) as WrapperException:
                print("Error while wrapping endpoint: ", WrapperException)
            except Exception as e:
                print('Exception: ', e)
