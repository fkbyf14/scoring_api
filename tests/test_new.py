import unittest

import mock as mock

from scoring import api, store
import redis
from scoring import store


class TestSuite(unittest.TestCase):
    def setUp(self):
        self.context = {}
        self.headers = {}
        self.store = None

    def get_response(self, request):
        return api.method_handler({"body": request, "headers": self.headers}, self.context, self.store)

    def test_empty_request(self):
        _, code = self.get_response({})
        self.assertEqual(api.INVALID_REQUEST, code)

    def test_broken_port(self):
        self.pool = redis.ConnectionPool(port=0)
        self.assertRaises(redis.ConnectionError)

    def test_get_nil_value(self):
        self.pool = redis.ConnectionPool(port=6379)
        cache = redis.StrictRedis(connection_pool=self.pool)
        result = cache.get('identifier1')
        self.assertEqual(None, result)

    def test_set_broken_value(self):
        self.pool = redis.ConnectionPool(port=6379)
        cache = redis.StrictRedis(connection_pool=self.pool)
        cache.set([1], 3)
        self.assertRaises(redis.DataError)

    def get_response_from_broken_port(self, request):
        self.store = store.Store('localhost', 9999, 0)
        return api.method_handler({"body": request, "headers": self.headers}, self.context, self.store)

    def test_request_to_broken_port(self):
        request = {"account": "horns&hoofs", "login": "h&f", "method": "online_score",
                   "arguments": {"gender": 2, "birthday": "01.01.2000"}}
        msg = self.get_response_from_broken_port(request)
        self.assertEqual(api.INVALID_REQUEST, msg)





if __name__ == "__main__":
    unittest.main()
