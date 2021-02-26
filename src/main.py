from src.Controller.database_controller import Database
from src.Controller.crawler_controller import Crawler
from src.Controller.sparql_controller import Sparql
from src.Util.link_filter import Filter

Database.initialize()
Sparql.endpoints_to_pool(
    Filter.triple_filtering(
        Crawler.all_search_engines()))
