import time

import redis
import logging

STORE_KEY = "interests"


class Store(object):

    def __init__(self, host, port, db):
        self.host = host
        self.port = port
        self.pool = []
        self.pool = self.get_conn()

        self.interests_cash = redis.StrictRedis(connection_pool=self.pool, socket_timeout=1)
        list_of_interests = ["cars", "pets", "travel", "hi-tech", "sport",
                             "music", "books", "tv", "cinema", "geek", "otus"]
        self.interests_cash.sadd(STORE_KEY, *list_of_interests)
        self.score_cash = redis.StrictRedis(connection_pool=self.pool, socket_timeout=1)

    def get_conn(self):
        if not self.pool:
            while True:
                try:
                    return redis.ConnectionPool(host=self.host, port=self.port, db=0)

                except redis.RedisError as e:
                    msg = "Cannot connect to Clients redis: %s" % e
                    logging.error(msg)
                    time.sleep(1)
        else:
            return self.pool

    def cache_get(self, key):
        response = self.score_cash.get(key)
        print "you are getting your cache: ", str(response)
        if response:
            return float(response)
        return response

    def cache_set(self, key, data, ex_time):
        print "you are setting:", str(data)
        self.score_cash.set(key, data, ex_time)

    def get(self, cid):
        #self.interests_cash.ping()
        try:
            response = self.interests_cash.srandmember(STORE_KEY, 2)
            return response
        except redis.ConnectionError as e:
            return e.args





