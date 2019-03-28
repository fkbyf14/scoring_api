import time

import redis
import logging

STORE_KEY = "interests"


class Store(object):

    def __init__(self, cache_server='localhost', port=6379, db_server='localhost'):
        self.host = cache_server
        self.port = port
        self.connection = []
        self.connection = self.get_conn()

        self.interests_cash = redis.StrictRedis(connection_pool=self.connection, socket_timeout=1)
        list_of_interests = ["cars", "pets", "travel", "hi-tech", "sport",
                             "music", "books", "tv", "cinema", "geek", "otus"]
        self.interests_cash.sadd(STORE_KEY, *list_of_interests)
        self.score_cash = redis.StrictRedis(connection_pool=self.connection, socket_timeout=1)

    def get_conn(self):
        if not self.connection:
            while True:
                try:
                    return redis.ConnectionPool(host=self.host, port=self.port, db=0)

                except redis.RedisError as e:
                    msg = "Cannot connect to Clients redis: %s" % e
                    logging.error(msg)
                    time.sleep(1)
        else:
            return self.connection

    def cache_get(self, key):
        response = self.score_cash.get(key)
        return response

    def cache_set(self, key, data, ex_time):
        self.score_cash.set(key, data, ex_time)

    def get(self, key):
        try:
            response = self.interests_cash.srandmember(STORE_KEY, 2)
            return response
        except redis.ConnectionError:
            raise





