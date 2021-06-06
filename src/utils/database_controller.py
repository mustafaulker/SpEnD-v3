import os
from datetime import datetime

import pymongo


class Database:
    DATABASE = None
    db = None

    def __init__(self):
        Database.DATABASE = self
        try:
            self.MONGODB_HOST = os.environ["MONGODB_HOST"]
            self.MONGODB_PORT = os.environ["MONGODB_PORT"]
            self.MONGODB_USERNAME = os.environ["MONGODB_USERNAME"]
            self.MONGODB_PASSWORD = os.environ["MONGODB_PASSWORD"]
            self.URI = f"mongodb://{self.MONGODB_HOST}:{self.MONGODB_PORT}/"
            # Authentication will be added.
            # self.URI = f"mongodb://{self.MONGODB_USERNAME}:{self.MONGODB_PASSWORD}" \
            #            f"@{self.MONGODB_HOST}:{self.MONGODB_PORT}/"
        except:
            print("Environment variables not found. Connecting to default URI")
            self.URI = "mongodb://localhost:27017/"

        client = pymongo.MongoClient(self.URI)
        self.db = client["SpEnD-DB"]

    @staticmethod
    def instance():
        if Database.DATABASE is None:
            Database()
        return Database.DATABASE

    def insert(self, collection: str, data):
        self.db[collection].insert(data)

    def insert_one(self, collection: str, data):
        self.db[collection].insert_one(data)

    def insert_many(self, collection: str, data):
        self.db[collection].insert_many(data)

    def find(self, collection: str, query, *args, **kwargs):
        return self.db[collection].find(query, *args, **kwargs)

    def find_one(self, collection: str, query, *args, **kwargs):
        return self.db[collection].find_one(query, *args, **kwargs)

    def update_one(self, collection: str, query, update):
        self.db[collection].update_one(query, update)

    def update_many(self, collection: str, query, update):
        self.db[collection].update_many(query, update)

    def delete_one(self, collection: str, query):
        self.db[collection].delete_one(query)

    def delete_many(self, collection: str, query):
        self.db[collection].delete_many(query)

    def drop_collection(self, collection: str):
        """
        Deletes the entire collection and it's data

        :param collection: Collection to be deleted
        :return: None
        """
        self.db.drop_collection(collection)

    def get_keywords(self, keys: str) -> tuple:
        """
        Gets keywords for desired keyword list.
        Possible params = ["crawl_keys", "inner_keys", "wanted_keys", "unwanted_keys"]

        :param keys: Desired keyword lists name
        :return: Tuple of keywords
        """
        all_keys = list(self.db['keywords'].find({}, {'_id': 0}))

        for i in range(len(all_keys)):
            if keys == list(all_keys[i].keys())[0]:
                return tuple(all_keys[i][keys])

    def get_endpoints(self) -> list:
        """
        Gathers all endpoints from endpoints collection except removed ones.

        :return: List of endpoints
        """
        endpoints = list()
        [endpoints.append(endpoint['url']) for endpoint
         in self.db['endpoints'].find({'tag': {'$not': {'$eq': 'removed'}}}, {'_id': 0, 'url': 1})]
        return endpoints

    def get_inner_domains(self) -> list:
        """
        Gathers all inner crawl domains from the database.

        :return: List of inner crawl domains
        """
        domains = list()
        [domains.append(domain) for domain in self.db['inner_domains'].find({})]
        return domains

    def insert_endpoint(self, link: str, link_domain: str, spider_name: str, keyword: str, page: int):
        """
        Inserts an endpoint to the endpoints collection.

        :param link: Endpoint's URL
        :param link_domain: Endpoint's domain
        :param spider_name: Which spider found the endpoint
        :param keyword: Which keyword found the endpoint
        :param page: On which page is the endpoint found
        :return: None
        """
        self.db['endpoints'].insert_one(
            {
                "url": link,
                "domain": link_domain,
                "date_created": datetime.utcnow(),
                "date_checked": datetime.utcnow(),
                "date_alive": datetime.utcnow(),
                "up_now": True,
                "tag": "pending",
                "spider": spider_name,
                "keyword": keyword,
                "page": page,
            })

    def insert_crawl_domain(self, link_domain: str):
        """
        Inserts a domain to the inner_domains collection.

        :param link_domain: Domain to be crawled
        :return: None
        """
        self.db['inner_domains'].insert_one(
            {
                "date_created": datetime.utcnow().strftime("%d-%m-%Y %H:%M:%S"),
                "domain": link_domain
            })

    def in_the_collection(self, collection: str, link_domain: str) -> bool:
        """
        Checks if given domain in the given collection or not.

        :param collection: Collection name for the domain to be sought for
        :param link_domain: Domain to be sought for
        :return: Boolean based on result
        """
        return self.db[collection].find_one({"domain": link_domain})

    def endpoint_alive_or_not(self, endpoint: str, up_now: bool):
        """
        Updates given endpoint's up status with given parameter.

        :param endpoint: URL of the endpoint to be updated
        :param up_now: State of endpoint
        :return: None
        """
        self.db['endpoints'].update_one(
            {"url": endpoint},
            {"$set": {"date_checked": datetime.utcnow(), "up_now": up_now}})

    def remove_keyword(self, keyword_array: str, keyword: str):
        """
        Deletes a keyword from specified keyword array.

        :param keyword_array: Array's name which contains specified keyword
        :param keyword: Keyword's name to be deleted
        :return: None
        """
        self.db['keywords'].update_one({keyword_array: keyword}, {'$pull': {keyword_array: keyword}})

    def insert_keyword(self, keyword_array: str, keyword):
        """
        Inserts keyword/s to specified keyword array.

        :param keyword_array: Array's name which keyword/s to be inserted.
        :param keyword: Keyword/s to be inserted.
        :return: None
        """
        self.db['keywords'].update_many(
            {keyword_array: {"$exists": True}}, {'$push': {keyword_array: {"$each": keyword}}})
