"""
No more ORM. It's too tricky to use.
The best is always the simplest.

Only one MongoClient (since it's thread-safe)
http://api.mongodb.com/python/current/faq.html?highlight=fork#is-pymongo-thread-safe
"""

from proxy_pool import settings
from proxy_pool.utils import print_log

from pymongo import MongoClient
from datetime import datetime
import random
import logging
import os


# todo: metaclass
client = MongoClient(host=settings.DB_HOST, port=settings.DB_PORT, maxPoolSize=500) # global

class Proxy:

    collection = client[settings.DB_NAME][settings.DB_COLLECTION]

    def __init__(self, value, count=1, update_time=datetime.now(), _id=None):
        self._id = _id
        self.value = value
        self.count = count
        self.update_time = update_time

    def __str__(self):
        return "<{}, count={}>".format(self.value, self.count)

    def __repr__(self):
        self.__str__()

    @classmethod
    def get(cls, criteria):
        """ Only return one proxy """
        proxy_dict = cls.collection.find_one(criteria)
        if proxy_dict:
            return cls(**proxy_dict)
        else:
            raise LookupError('Object does not exist')

    @classmethod
    def filter(cls, criteria):
        """ Get a list of proxies 
        WARNING: It might not be used to check if a certain value exists
        """
        for proxy_dict in cls.collection.find(criteria).sort('count'):
            yield cls(**proxy_dict)

    def save(self):
        proxy_dict = self.__dict__
        if self.collection.find_one({'_id': self._id}):
            self.collection.update({'_id': self._id}, {'$set': proxy_dict})
        else:
            proxy_dict.pop('_id')
            self.collection.insert(proxy_dict)

    def delete(self):
        self.collection.find_one_and_delete({'_id': self._id})

    @classmethod
    def aggregate(cls, criteria):
        """
        It's the same as something like:
        `collection.aggregate([{ "$sort" : { "update_time": 1 } }])`,
        where [{ "$sort" : { "update_time": 1 } }] is the criteria
        """
        for proxy_dict in cls.collection.aggregate(criteria):
            yield cls(**proxy_dict)

    @classmethod
    def total(cls):
        """ return the total number of proxies """
        return cls.collection.count_documents({})

    @classmethod
    def valid(cls):
        """return the number of valid proxies
        I define them by count <= 1
        """
        return cls.collection.find({"count": {"$lte": 1}}).count()

    @classmethod
    def random(cls, max_count=2):
        """ random proxy object with count less than a number 
        This is slow because it loads all proxies with certain count
        into memory; I'll improve this later
        """
        proxies = cls.collection.find({'count': {'$lte': max_count}})
        proxy_dict = random.choices(list(proxies))[0]
        return cls(**proxy_dict)

    @classmethod
    def quality_rate(cls):
        """Check the quality of proxy pool. If the quality is bad, 
        the pool will boost its updating speed
        """

        good = cls.collection.find({"count": 0}).count()
        bad = cls.collection.find({"count": {"$gt": 0}}).count() 
        return good / (bad + good)

    def status(self, *info):
        content = '{:<22} update: {:<12}total: {:<6}valid: {}   -> {}'.format(
            self.value,
            self.update_time.strftime("%H:%M:%S"),
            self.total(),
            self.valid(),
            ' '.join([str(i) for i in info])
        )
        print_log(content)





