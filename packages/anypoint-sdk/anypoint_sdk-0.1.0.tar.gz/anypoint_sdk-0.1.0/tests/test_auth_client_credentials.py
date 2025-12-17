# tests/test_auth_client_credentials.py
import unittest

from anypoint_sdk._http import HttpClient
from anypoint_sdk.auth import TokenAuth, get_token_with_client_credentials
from tests.fakes import FakeSession
from tests.helpers import make_response

BASE = "https://api.test.local"


class ClientCredentialsTests(unittest.TestCase):
    def test_get_token_with_client_credentials(self):
        token_resp = make_response(
            status=200,
            json_body={
                "access_token": "abc123",
                "token_type": "bearer",
                "expires_in": 3600,
            },
            url=f"{BASE}/accounts/api/v2/oauth2/token",
        )
        fake = FakeSession([token_resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        token = get_token_with_client_credentials(http, "id", "secret")
        self.assertEqual(token.access_token, "abc123")
        self.assertEqual(fake.calls[0]["json"]["grant_type"], "client_credentials")
        self.assertEqual(fake.calls[0]["json"]["client_id"], "id")

    def test_get_bad_token_with_client_credentials(self):
        token_resp = make_response(
            status=200,
            json_body={"error": "failed to get token"},
            url=f"{BASE}/accounts/api/v2/oauth2/token",
        )
        fake = FakeSession([token_resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        with self.assertRaisesRegex(ValueError, "Token response missing access_token"):
            get_token_with_client_credentials(http, "id", "secret")

    def test_get_auth_headers(self):
        token_resp = make_response(
            status=200,
            json_body={
                "access_token": "abc123",
                "token_type": "bearer",
                "expires_in": 3600,
            },
            url=f"{BASE}/accounts/api/v2/oauth2/token",
        )
        fake = FakeSession([token_resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)
        token = get_token_with_client_credentials(http, "id", "secret")

        auth = TokenAuth(token=token.access_token)
        self.assertEqual(
            auth.as_header(), {"Authorization": f"Bearer {token.access_token}"}
        )


if __name__ == "__main__":
    unittest.main()
