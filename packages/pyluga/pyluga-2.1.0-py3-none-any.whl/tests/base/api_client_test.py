import unittest

from pyluga.exceptions import ClientConfigError
from pyluga import api_client


class ApiClientTests(unittest.TestCase):

    def test_beluga_client_raises_without_required_params(self):
        with self.assertRaises(ClientConfigError):
            api_client.BelugaClient(api_key='key', url=None)
        with self.assertRaises(ClientConfigError):
            api_client.BelugaClient(api_key=None, url='url')
