# tests/test_client_from_client_credentials.py
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from anypoint_sdk.client import DEFAULT_USER_AGENT, AnypointClient

BASE = "https://api.test.local"


class _ListLogger:
    # Minimal LoggerLike for injection
    def __init__(self, name: str = "test"):
        self.name = name

    def debug(self, msg, *a, **k):
        pass

    def info(self, msg, *a, **k):
        pass

    def warning(self, msg, *a, **k):
        pass

    def error(self, msg, *a, **k):
        pass

    def child(self, suffix: str):
        return self


class FakeHttpClient:
    instances: list["FakeHttpClient"] = []

    def __init__(self, *, base_url, headers, timeout, verify, cert, proxies):
        self.base_url = base_url
        self.headers = dict(headers)
        self.timeout = timeout
        self.verify = verify
        self.cert = cert
        self.proxies = proxies
        self.closed = False
        FakeHttpClient.instances.append(self)

    def close(self):
        self.closed = True


class FromClientCredentialsTests(unittest.TestCase):
    def setUp(self) -> None:
        FakeHttpClient.instances.clear()

    @patch("anypoint_sdk.client.get_token_with_client_credentials")
    @patch("anypoint_sdk.client.HttpClient", new=FakeHttpClient)
    def test_success_builds_client_closes_bootstrap_and_passes_args(
        self, mock_get_token
    ):
        # Arrange: fake token
        mock_get_token.side_effect = (
            lambda http, client_id, client_secret: SimpleNamespace(
                access_token="abc123"
            )
        )
        extra_headers = {"X-Test": "1"}
        logger = _ListLogger("scanner")

        # Act
        client = AnypointClient.from_client_credentials(
            "cid",
            "csec",
            base_url=BASE,
            timeout=5.0,
            verify=False,
            cert=("c.crt", "c.key"),
            proxies={"https": "http://proxy"},
            extra_headers=extra_headers,
            logger=logger,
        )

        # Assert: HttpClient was constructed twice, bootstrap then main
        self.assertEqual(len(FakeHttpClient.instances), 2)
        bootstrap, main = FakeHttpClient.instances

        # Bootstrap got the right params and UA merge
        self.assertEqual(bootstrap.base_url, BASE)
        self.assertEqual(bootstrap.timeout, 5.0)
        self.assertFalse(bootstrap.verify)
        self.assertEqual(bootstrap.cert, ("c.crt", "c.key"))
        self.assertEqual(bootstrap.proxies, {"https": "http://proxy"})
        self.assertEqual(bootstrap.headers["User-Agent"], DEFAULT_USER_AGENT)
        self.assertEqual(bootstrap.headers["X-Test"], "1")

        # Bootstrap was closed in finally
        self.assertTrue(bootstrap.closed)

        # Token fetch was called with bootstrap and creds
        mock_get_token.assert_called_once()
        args, kwargs = mock_get_token.call_args
        self.assertIs(args[0], bootstrap)
        self.assertEqual(kwargs["client_id"], "cid")
        self.assertEqual(kwargs["client_secret"], "csec")

        # Returned client is an AnypointClient, and main transport has auth header
        self.assertIsInstance(client, AnypointClient)
        self.assertEqual(main.base_url, BASE)
        self.assertEqual(main.headers["User-Agent"], DEFAULT_USER_AGENT)
        # Authorization header created by __init__ using the token
        self.assertEqual(main.headers["Authorization"], "Bearer abc123")
        # Extra headers persist on main client as well
        self.assertEqual(main.headers["X-Test"], "1")

        client.close()  # clean up

    @patch("anypoint_sdk.client.get_token_with_client_credentials")
    @patch("anypoint_sdk.client.HttpClient", new=FakeHttpClient)
    def test_error_path_still_closes_bootstrap_and_reraises(self, mock_get_token):
        # Arrange: token fetch raises
        mock_get_token.side_effect = RuntimeError("boom")

        with self.assertRaises(RuntimeError):
            AnypointClient.from_client_credentials("cid", "csec", base_url=BASE)

        # Even though it failed before constructing the main client, bootstrap should exist and be closed
        self.assertEqual(len(FakeHttpClient.instances), 1)
        bootstrap = FakeHttpClient.instances[0]
        self.assertTrue(bootstrap.closed)


if __name__ == "__main__":
    unittest.main()
