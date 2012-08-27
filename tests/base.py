import os
import unittest

from google.appengine.ext import testbed

class TestbedTest(unittest.TestCase):

    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_user_stub()
        self.testbed.init_memcache_stub()

        self.testbed.setup_env(
            USER_EMAIL = 'test@gae.com',
            USER_ID = '22222',
            USER_IS_ADMIN = '1',
            overwrite = True)

    def tearDown(self):
        self.testbed.deactivate()
