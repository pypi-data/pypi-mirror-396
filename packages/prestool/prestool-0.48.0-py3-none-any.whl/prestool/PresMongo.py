from pymongo import MongoClient, ASCENDING, DESCENDING
from contextlib import contextmanager


class PresMongo:
    def __init__(self):
        self.mongo_host = ''
        self.mongo_port = 27017
        self.mongo_user = ''
        self.mongo_pwd = ''
        self.mongo_db_name = ''
        self.mongo_auth_source = ''

    @contextmanager
    def conn_mongo(self, table):
        url = f'mongodb://{self.mongo_user}:{self.mongo_pwd}@{self.mongo_host}:{self.mongo_port}/'
        if self.mongo_auth_source:
            url += f'?authSource={self.mongo_auth_source}'
        mongo_client = MongoClient(url)
        db = mongo_client[self.mongo_db_name]
        collection = db[table]
        try:
            yield collection
        finally:
            mongo_client.close()

    def to_query(self, table, where, is_all=False, asc=None, desc=None, limit=None):
        with self.conn_mongo(table) as collection:
            if is_all:
                res = collection.find(where)
            else:
                res = collection.find_one(where)
            if asc:
                res = res.sort(asc, ASCENDING)
            if desc:
                res = res.sort(desc, DESCENDING)
            if limit:
                res = res.limit(limit)
            return list(res) if is_all else res

    def to_update(self, table, target, where):
        with self.conn_mongo(table) as collection:
            collection.update_many(where, {'$set': target})

    def to_delete(self, table, where):
        with self.conn_mongo(table) as collection:
            collection.delete_many(where)

    def to_insert(self, table, target, is_list=False):
        with self.conn_mongo(table) as collection:
            if is_list:
                collection.insert_many(target)
            else:
                collection.insert_one(target)