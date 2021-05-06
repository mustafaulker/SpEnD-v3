import os
from datetime import datetime

import pymongo


class Database:
    try:
        MONGODB_HOST = os.environ["MONGODB_HOST"]
        MONGODB_PORT = os.environ["MONGODB_PORT"]
        MONGODB_USERNAME = os.environ["MONGODB_USERNAME"]
        MONGODB_PASSWORD = os.environ["MONGODB_PASSWORD"]
        URI = f"mongodb://{MONGODB_HOST}:{MONGODB_PORT}/"
        # Authentication will be added.
        # URI = f"mongodb://{MONGODB_USERNAME}:{MONGODB_PASSWORD}@{MONGODB_HOST}:{MONGODB_PORT}/"
    except:
        print("Environment variables not found. Connecting to default URI")
        URI = "mongodb://localhost:27017/"

    DATABASE = None

    @staticmethod
    def initialize():
        client = pymongo.MongoClient(Database.URI)
        Database.DATABASE = client["SpEnD-DB"]

    @staticmethod
    def insert(collection: str, data):
        Database.DATABASE[collection].insert(data)

    @staticmethod
    def insert_one(collection: str, data):
        Database.DATABASE[collection].insert_one(data)

    @staticmethod
    def insert_many(collection: str, data):
        Database.DATABASE[collection].insert_many(data)

    @staticmethod
    def find(collection: str, query, *args, **kwargs):
        return Database.DATABASE[collection].find(query, *args, **kwargs)

    @staticmethod
    def find_one(collection: str, query, *args, **kwargs):
        return Database.DATABASE[collection].find_one(query, *args, **kwargs)

    @staticmethod
    def drop_collection(collection: str):
        """

        :param collection:
        :return:
        """
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
    def update(collection: str, query, update):
        Database.DATABASE[collection].update_one(query, update)

    @staticmethod
    def delete_one(collection: str, query):
        Database.DATABASE[collection].delete_one(query)

    @staticmethod
    def delete_many(collection: str, query):
        Database.DATABASE[collection].delete_many(query)

    @staticmethod
    def get_endpoints() -> list:
        """
        Gathers all endpoints from endpoints collection except removed ones.

        :return: List of endpoints
        """
        endpoints = list()
        [endpoints.append(endpoint["url"]) for endpoint
         in Database.find("endpoints", {"tag": {"$not": {"$eq": "removed"}}}, {"_id": 0, "url": 1})]
        return endpoints

    @staticmethod
    def get_second_crawl_domains() -> list:
        """
        Gathers all second crawl domains from the database.

        :return: List of second crawl domains
        """
        domains = list()
        [domains.append(domain) for domain in Database.find("second_crawl_domains", {})]
        return domains

    @staticmethod
    def insert_endpoint(link: str, link_domain: str):
        """
        Inserts an endpoint to the endpoints collection.

        :param link: Endpoint's URL
        :param link_domain: Endpoint's domain
        :return: None
        """
        Database.insert_one("endpoints", {
            "url": link,
            "domain": link_domain,
            "date_created": datetime.utcnow(),
            "date_checked": datetime.utcnow(),
            "date_alive": datetime.utcnow(),
            "up_now": True,
            "tag": "pending",
        })

    @staticmethod
    def insert_crawl_domain(link_domain: str):
        """
        Inserts a domain to the second_crawl_domain collection.

        :param link_domain: Domain to be crawled
        :return: None
        """
        Database.insert_one("second_crawl_domains",
                            {"date_created": datetime.utcnow().strftime("%d-%m-%Y %H:%M:%S"),
                             "domain": link_domain})

    @staticmethod
    def in_the_collection(collection: str, link_domain: str) -> bool:
        """
        Checks if given domain in the given collection or not.

        :param collection: Collection name for the domain to be sought for
        :param link_domain: Domain to be sought for
        :return: Boolean based on result
        """
        return Database.find_one(collection, {"domain": link_domain})

    @staticmethod
    def endpoint_alive_or_not(endpoint: str, up_now: bool):
        """
        Updates given endpoint's up status with given parameter.

        :param endpoint: URL of the endpoint to be updated
        :param up_now: State of endpoint
        :return: None
        """
        Database.update("endpoints", {"url": endpoint},
                        {"$set": {"date_checked": datetime.utcnow(), "up_now": up_now}})
