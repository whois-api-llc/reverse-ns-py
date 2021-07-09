import os
import unittest
from reversens import Client
from reversens import ParameterError, ApiAuthError

name_server1 = 'ns2.google.com'
name_server2 = 'carl.ns.cloudflare.com'


class TestClient(unittest.TestCase):
    """
    Final integration tests without mocks.

    Active API_KEY is required.
    """
    def setUp(self) -> None:
        self.client = Client(os.getenv('API_KEY'))

    def test_get_correct_data(self):
        response = self.client.get(ns=name_server2)
        self.assertGreater(len(response.result), 0, "Empty result in response")

    def test_extra_parameters(self):
        response = self.client.get(ns=name_server2, search_from='b')
        self.assertGreater(len(response.result), 1)

    def test_empty_terms(self):
        with self.assertRaises(ParameterError):
            self.client.get('')

    def test_incorrect_api_key(self):
        client = Client('at_00000000000000000000000000000')
        with self.assertRaises(ApiAuthError):
            client.get(ns=name_server2)

    def test_raw_data(self):
        response = self.client.get_raw(
            ns=name_server2, output_format=Client.XML_FORMAT)
        self.assertTrue(response.startswith('<?xml'))

    def test_iteration(self):
        self.client.name_server = name_server1
        cnt = 0
        for page in self.client:
            if cnt >= 3:
                break
            self.assertGreater(len(page.result), 0)
            cnt += 1


if __name__ == '__main__':
    unittest.main()
