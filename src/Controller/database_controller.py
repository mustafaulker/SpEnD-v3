import pymongo


class Database:
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
    def find(collection, query):
        return Database.DATABASE[collection].find(query)

    @staticmethod
    def find_one(collection, query):
        return Database.DATABASE[collection].find_one(query)

    @staticmethod
    def drop_collection(collection):
        Database.DATABASE.drop_collection(collection)
