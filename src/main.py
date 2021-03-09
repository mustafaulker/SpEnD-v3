from src.Controller.database_controller import Database
from src.Controller.crawler_controller import Crawler
from src.Controller.sparql_controller import Sparql

Database.initialize()

# First Crawl
Crawler.all_search_engines(1, Database.get_keywords("crawl_keys"))

domains_to_recrawl = Database.get_domains() - Database.get_endpoints()
recrawl_keys = Database.get_keywords('recrawl_keys')

# Second Crawl
for domain in domains_to_recrawl:
    for key in recrawl_keys:
        Crawler.all_search_engines(2, f"{key} site:{domain}")

Sparql.endpoints_to_pool(Database.get_recrawl_links() - Database.get_endpoints())
