# tests/test_client_context.py
import unittest
from unittest.mock import MagicMock

from anypoint_sdk.client import AnypointClient

BASE = "https://api.test.local"


class AnypointClientContextTests(unittest.TestCase):
    def _make_client(self) -> AnypointClient:
        # Token constructor does not issue HTTP calls
        return AnypointClient(token="test-token", base_url=BASE, timeout=1)

    def test_context_manager_returns_self_and_calls_close(self):
        client = self._make_client()
        client.close = MagicMock()  # spy on close()

        with client as cm:
            self.assertIs(cm, client)  # __enter__ returns self

        client.close.assert_called_once_with()  # __exit__ called close()

    def test_context_manager_calls_close_on_exception_and_reraises(self):
        client = self._make_client()
        client.close = MagicMock()

        class Boom(Exception):
            pass

        with self.assertRaises(Boom):
            with client:
                raise Boom("boom")  # exception should propagate

        client.close.assert_called_once_with()

    def test_close_delegates_to_http_close(self):
        client = self._make_client()
        mock_http = MagicMock()
        client._http = mock_http  # replace internal transport for test

        client.close()

        mock_http.close.assert_called_once_with()

    def test_close_propagates_exception_from_http(self):
        client = self._make_client()
        mock_http = MagicMock()
        mock_http.close.side_effect = RuntimeError("boom")
        client._http = mock_http

        with self.assertRaises(RuntimeError):
            client.close()

        mock_http.close.assert_called_once_with()

    def test_get_token_returns_bearer_token(self):
        client = self._make_client()
        token = client.get_token()
        self.assertEqual(token, "test-token")

    def test_get_token_strips_bearer_prefix(self):
        client = AnypointClient(token="my-secret-token", base_url=BASE, timeout=1)
        token = client.get_token()
        self.assertEqual(token, "my-secret-token")
        self.assertNotIn("Bearer", token)


if __name__ == "__main__":
    unittest.main()
