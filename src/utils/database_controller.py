import pymongo
import os
from datetime import datetime


class Database:
    try:
        mongohost = os.environ["MONGODB_HOST"]
        mongoport = os.environ["MONGODB_PORT"]
        mongouser = os.environ["MONGODB_USERNAME"]
        mongopass = os.environ["MONGODB_PASSWORD"]
        URI = f"mongodb://{mongohost}:{mongoport}/"
        # Authentication will be added.
        # URI = f"mongodb://{mongouser}:{mongopass}@{mongohost}:{mongoport}/"
    except:
        print("Environment variables not found. Connecting to default URI")
        URI = "mongodb://localhost:27017/"

    DATABASE = None

    @staticmethod
    def initialize():
        client = pymongo.MongoClient(Database.URI)
        Database.DATABASE = client["SpEnD-DB"]

    @staticmethod
    def insert(collection, data):
        Database.DATABASE[collection].insert(data)

    @staticmethod
    def insert_one(collection, data):
        Database.DATABASE[collection].insert_one(data)

    @staticmethod
    def insert_many(collection, data):
        Database.DATABASE[collection].insert_many(data)

    @staticmethod
    def find(collection, query, *args, **kwargs):
        return Database.DATABASE[collection].find(query, *args, **kwargs)

    @staticmethod
    def find_one(collection, query, *args, **kwargs):
        return Database.DATABASE[collection].find_one(query, *args, **kwargs)

    @staticmethod
    def drop_collection(collection):
        Database.DATABASE.drop_collection(collection)

    @staticmethod
    def get_keywords(keys) -> list:
        """
        Gets keywords for desired keyword list.
        Possible params = ["crawl_keys", "second_crawl_keys", "wanted_keys", "unwanted_keys"]

        :param keys: Desired keyword lists name
        :return: List of keywords
        """
        all_keys = list(Database.DATABASE["keywords"].find({}, {"_id": 0}))

        for i in range(len(all_keys)):
            if keys == list(all_keys[i].keys())[0]:
                return all_keys[i][keys]

    @staticmethod
    def get_endpoints():
        endpoints = list()
        [endpoints.append(endpoint["url"]) for endpoint
         in Database.find("endpoints", {}, {"_id": 0, "url": 1})]
        return endpoints

    @staticmethod
    def get_second_crawl_domains():
        domains = list()
        [domains.append(domain["domain"]) for domain
         in Database.find("second_crawl_domains", {}, {"_id": 0, "domain": 1})]
        return domains

    @staticmethod
    def insert_to_endpoints_collection(link: str, link_domain: str):
        Database.insert_one("endpoints",
                            {"date_created": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                             "url": link,
                             "domain": link_domain})

    @staticmethod
    def insert_to_second_crawl_domains_collection(link_domain: str):
        Database.insert_one("second_crawl_domains",
                            {"date_created": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                             "domain": link_domain})

    @staticmethod
    def in_the_endpoints_collection(link_domain: str) -> bool:
        return Database.find_one("endpoints", {"domain": link_domain})

    @staticmethod
    def in_the_second_crawl_domains_collection(link_domain: str) -> bool:
        return Database.find_one("second_crawl_domains", {"domain": link_domain})
