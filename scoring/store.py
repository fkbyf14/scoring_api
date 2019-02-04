import redis
import json

#POOL = redis.ConnectionPool(host='localhost', port=6379, db=0)
STORE_KEY = "interests"

class Store(object):

    def __init__(self, host, port, db):
        self.pool = redis.ConnectionPool(host=host, port=port, db=db)
        self.interests_cash = redis.Redis(connection_pool=self.pool)
        list_of_interests = ["cars", "pets", "travel", "hi-tech", "sport", "music", "books", "tv", "cinema", "geek", "otus"]
        self.interests_cash.sadd(STORE_KEY, *list_of_interests)


    def cache_get(self, key):
        my_server = redis.Redis(connection_pool=self.pool)
        response = my_server.get(key)
        print "you are getting your cache: ", str(response)
        if response:
            return float(response)
        return response


    def cache_set(self, key, data, ex_time):
        my_server = redis.Redis(connection_pool=self.pool)
        print "you are setting:", str(data)
        my_server.set(key, data, ex_time)



    def get(self, cid):
        # my_server = redis.Redis(connection_pool=self.pool)
        #print self.interests_cash.type('i')
        #print self.interests_cash.info()
        response = self.interests_cash.srandmember(STORE_KEY, 2)
        print "you are getting: ", str(response)
        return response



# create a connection to the localhost Redis server instance, by
# default it runs on port 6379
"""redis_db = redis.StrictRedis(host="localhost", port=6379, db=1)
# see what keys are in Redis
print redis_db.keys()
# output for keys() should be an empty list "[]"

print redis_db.set('full stack', 'python')
# output should be "True"
#redis_db.keys()
# now we have one key so the output will be "[b'full stack']"
print redis_db.get('full stack')
# output is "b'python'", the key and value still exist in Redis
redis_db.incr('twilio')
# output is "1", we just incremented even though the key did not
# previously exist
redis_db.get('twilio')
# output is "b'1'" again, since we just obtained the value from
# the existing key
redis_db.delete('twilio')
# output is "1" because the command was successful
redis_db.get('twilio')
# nothing is returned because the key and value no longer exist
"""