import os
import random
import unittest
import uuid

from scoring.store import Store

DEAD_SERVER_IP = '192.0.2.1'


@unittest.skipIf('SKIP_TEST_MEMCACHED' in os.environ, 'environment variable is set to skip')
class TestCacheStorage(unittest.TestCase):

    def test_sequential_set_and_get(self):
        self.store = Store()
        key = uuid.uuid4().hex
        value = str(random.random())
        self.store.cache_set(key, value, 60*60)
        self.assertEqual(value, self.store.cache_get(key))

    def test_get_by_not_existing_key(self):
        self.store = Store()
        key = uuid.uuid4().hex
        self.assertIsNone(self.store.cache_get(key))

    def test_get_when_server_down(self):
        self.store = Store(cache_server=DEAD_SERVER_IP)
        key = uuid.uuid4().hex
        with self.assertRaises(Exception):
            self.store.get(key)

    def test_set_when_server_down(self):
        self.store = Store(cache_server=DEAD_SERVER_IP)
        key = uuid.uuid4().hex
        self.store.cache_set(key, 1)
        self.assertIsNone(None, self.store.cache_get(key))


@unittest.skipIf('SKIP_TEST_REDIS' in os.environ, 'environment variable is set to skip')
class TestPersistentStorage(unittest.TestCase):

    def test_sequential_set_and_get(self):
        self.store = Store()
        key = uuid.uuid4().hex
        value = str(random.random())
        self.store.set(key, value)
        self.assertEqual(value, self.store.get(key))

    def test_get_by_not_existing_key(self):
        self.store = Store()
        key = uuid.uuid4().hex
        self.assertEqual(None, self.store.get(key))

    def test_get_when_server_down(self):
        self.store = Store(db_server=DEAD_SERVER_IP)
        key = uuid.uuid4().hex
        with self.assertRaises(Exception):
            self.store.get(key)

    def test_set_when_server_down(self):
        self.store = Store(db_server=DEAD_SERVER_IP)
        key = uuid.uuid4().hex
        with self.assertRaises(Exception):
            self.store.set(key, 1)

