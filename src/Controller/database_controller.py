import pymongo
from urllib.parse import urlparse
import os


class Database:
    try:
        mongohost = os.environ['MONGODB_HOST']
        mongoport = os.environ['MONGODB_PORT']
        mongouser = os.environ['MONGODB_USERNAME']
        mongopass = os.environ['MONGODB_PASSWORD']
        URI = f"mongodb://{mongohost}:{mongoport}/"
        # Authentication will be added.
        # URI = f"mongodb://{mongouser}:{mongopass}@{mongohost}:{mongoport}/"
    except:
        print('Environment variables not found. Connecting to default URI')
        URI = 'mongodb://localhost:27017/'

    DATABASE = None

    @staticmethod
    def initialize():
        client = pymongo.MongoClient(Database.URI)
        Database.DATABASE = client['SpEnD-DB']

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
    def get_keywords(keys):
        """
        Gets keywords for desired keyword list.
        Possible params = ["crawl_keys", "recrawl_keys", "wanted_keys", "unwanted_keys"]

        :param keys: Desired keyword lists name
        :return: List of keywords
        """
        all_keys = list(Database.DATABASE["Keywords"].find({}, {'_id': 0}))

        for i in range(len(all_keys)):
            if keys == list(all_keys[i].keys())[0]:
                return all_keys[i][keys]

    @staticmethod
    def get_endpoints():
        endpoints = []
        [endpoints.append(urlparse(endpoint['url']).netloc) for endpoint
         in Database.find('Endpoints', {}, {'_id': 0, 'url': 1})]
        return set(endpoints)

    @staticmethod
    def get_domains():
        domains = []
        [domains.append(domain['domain']) for domain
         in Database.find('Domains', {}, {'_id': 0, 'domain': 1})]
        return set(domains)

    @staticmethod
    def get_recrawl_links():
        recrawl_links = []
        [recrawl_links.append(recrawl_link['rc_url']) for recrawl_link
         in Database.find('ReCrawl_Links', {}, {'_id': 0, 'rc_url': 1})]
        return set(recrawl_links)
