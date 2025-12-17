import unittest

from anypoint_sdk._http import HttpClient, HttpError
from anypoint_sdk.resources.applications import Applications
from tests.fakes import FakeSession
from tests.helpers import make_response

BASE = "https://api.test.local"


class ApplicationsCreateTests(unittest.TestCase):
    def test_create_minimal_application_success(self):
        org_id = "o1"
        app_name = "test-app"

        created_app = {
            "id": 12345,
            "name": app_name,
            "clientId": "abc123-def456",
            "clientSecret": "secret789",
            "apiEndpoints": False,
        }

        resp = make_response(
            status=200,
            json_body=created_app,
            url=f"{BASE}/apiplatform/repository/v2/organizations/{org_id}/applications",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        result = Applications(http).create(org_id, app_name)

        self.assertEqual(len(fake.calls), 1)
        call = fake.calls[0]
        self.assertEqual(call["method"], "POST")
        self.assertEqual(
            call["url"],
            f"{BASE}/apiplatform/repository/v2/organizations/{org_id}/applications",
        )

        expected_payload = {
            "name": app_name,
            "apiEndpoints": False,
        }
        self.assertEqual(call["json"], expected_payload)
        self.assertEqual(result, created_app)

    def test_create_full_application_with_all_options(self):
        org_id = "o1"
        app_name = "full-test-app"
        description = "A test application"
        url = "https://example.com/app"
        grant_types = ["client_credentials", "authorization_code"]
        redirect_uris = ["https://example.com/callback"]

        created_app = {"id": 67890, "name": app_name}

        resp = make_response(
            status=200,
            json_body=created_app,
            url=f"{BASE}/apiplatform/repository/v2/organizations/{org_id}/applications",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        Applications(http).create(
            org_id,
            app_name,
            description=description,
            url=url,
            grant_types=grant_types,
            redirect_uris=redirect_uris,
            api_endpoints=True,
        )

        call = fake.calls[0]
        expected_payload = {
            "name": app_name,
            "description": description,
            "url": url,
            "grantTypes": grant_types,
            "redirectUri": redirect_uris,
            "apiEndpoints": True,
        }
        self.assertEqual(call["json"], expected_payload)

    def test_create_application_handles_400_bad_request(self):
        org_id = "o1"
        resp = make_response(
            status=400,
            text="Bad Request",
            url=f"{BASE}/apiplatform/repository/v2/organizations/{org_id}/applications",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        with self.assertRaises(HttpError) as ctx:
            Applications(http).create(org_id, "test-app")

        self.assertEqual(ctx.exception.status, 400)

    def test_create_application_handles_empty_response(self):
        org_id = "o1"
        resp = make_response(
            status=200,
            text="",
            url=f"{BASE}/apiplatform/repository/v2/organizations/{org_id}/applications",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        result = Applications(http).create(org_id, "test-app")
        self.assertEqual(result, {})


if __name__ == "__main__":
    unittest.main()
