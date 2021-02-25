from src.Controller.database_controller import Database
from src.Controller.crawler_controller import Crawler
from src.Controller.sparql_controller import Sparql

Database.initialize()
Sparql.is_endpoint(Crawler.multiple_search_engine("google_engine", "bing_engine"))
