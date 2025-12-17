# tests/test_applications.py
import unittest

from anypoint_sdk._http import HttpClient
from anypoint_sdk.resources.applications import Applications
from tests.fakes import FakeSession
from tests.helpers import make_response

BASE = "https://api.test.local"


class ApplicationsTests(unittest.TestCase):
    def test_list_normalises_captures_credentials_and_dedupes(self):
        org_id = "o1"
        payload = {
            "applications": [
                {
                    "audit": {
                        "created": {"date": "2025-08-15T09:34:36.561Z"},
                        "updated": {},
                    },
                    "id": 2693831,
                    "name": "treasury-app-1",
                    "description": None,
                    "coreServicesId": "f3f1e789327f4d41b3bcbc9890764ae4",
                    "url": None,
                    "clientId": "f3f1e789327f4d41b3bcbc9890764ae4",
                    "clientSecret": "c58c08f1702E49dAb27771887D93A4A5",
                    "grantTypes": [],
                    "redirectUri": [],
                    "owner": "Mule User",
                    "email": "mule-user-1@proton.me",
                    "owners": [
                        {
                            "id": "2a0...",
                            "organizationId": "o1",
                            "firstName": "Mule",
                            "lastName": "User",
                            "email": "mule-user-1@proton.me",
                            "username": "mule-user-1",
                            "entityType": "user",
                        },
                        "bad",  # ignored
                    ],
                },
                # duplicate id to prove dedupe
                {"id": 2693831, "name": "dupe"},
            ],
            "total": 2,
        }
        resp = make_response(
            status=200,
            json_body=payload,
            url=f"{BASE}/apiplatform/repository/v2/organizations/{org_id}/applications",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        out = Applications(http).list(org_id)

        self.assertEqual(len(out), 1)
        app = out[0]
        self.assertEqual(app["id"], 2693831)
        self.assertEqual(app["name"], "treasury-app-1")
        self.assertEqual(app["clientId"], "f3f1e789327f4d41b3bcbc9890764ae4")
        self.assertEqual(app["clientSecret"], "c58c08f1702E49dAb27771887D93A4A5")
        self.assertEqual(app["ownerName"], "Mule User")
        self.assertEqual(app["ownerEmail"], "mule-user-1@proton.me")
        self.assertIsInstance(app["owners"], list)
        # Confirm the query param was set
        self.assertEqual(fake.calls[0]["params"]["targetAdminSite"], "true")

    def test_list_handles_missing_or_wrong_shape(self):
        org_id = "o1"
        # No 'applications' key
        resp1 = make_response(
            status=200,
            json_body={"total": 0},
            url=f"{BASE}/apiplatform/repository/v2/organizations/{org_id}/applications",
        )
        http1 = HttpClient(base_url=BASE, session=FakeSession([resp1]), retries=0)
        out1 = Applications(http1).list(org_id)
        self.assertEqual(out1, [])

        # 'applications' is wrong type
        resp2 = make_response(
            status=200,
            json_body={"applications": {"unexpected": True}},
            url=f"{BASE}/apiplatform/repository/v2/organizations/{org_id}/applications",
        )
        http2 = HttpClient(base_url=BASE, session=FakeSession([resp2]), retries=0)
        out2 = Applications(http2).list(org_id)
        self.assertEqual(out2, [])

    def test_list_ignores_non_dict_and_normalises_lists(self):
        org_id = "o1"
        payload = {
            "applications": [
                "bad",
                123,
                {
                    "id": 1,
                    "name": "app-1",
                    "grantTypes": ["client_credentials", 7, None],
                    "redirectUri": ["https://a.example/cb", {"oops": True}],
                },
            ]
        }
        resp = make_response(
            status=200,
            json_body=payload,
            url=f"{BASE}/apiplatform/repository/v2/organizations/{org_id}/applications",
        )
        http = HttpClient(base_url=BASE, session=FakeSession([resp]), retries=0)
        out = Applications(http).list(org_id)

        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["grantTypes"], ["client_credentials"])
        self.assertEqual(out[0]["redirectUri"], ["https://a.example/cb"])

    def test_list_allows_disabling_target_admin_site(self):
        org_id = "o1"
        resp = make_response(
            status=200,
            json_body={"applications": []},
            url=f"{BASE}/apiplatform/repository/v2/organizations/{org_id}/applications",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        Applications(http).list(org_id, target_admin_site=False)

        self.assertEqual(fake.calls[0]["params"]["targetAdminSite"], "false")

    def test_create_basic(self):
        org_id = "o1"
        payload = {
            "id": 2693832,
            "name": "test-app",
            "clientId": "abc123",
            "clientSecret": "secret456",
        }
        resp = make_response(
            status=200,
            json_body=payload,
            url=f"{BASE}/apiplatform/repository/v2/organizations/{org_id}/applications",
        )
        session = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=session, retries=0)

        result = Applications(http).create(org_id, "test-app")

        self.assertEqual(result["id"], 2693832)
        self.assertEqual(result["name"], "test-app")
        self.assertEqual(result["clientId"], "abc123")
        # Verify request payload
        self.assertEqual(session.calls[0]["json"]["name"], "test-app")
        self.assertEqual(session.calls[0]["json"]["apiEndpoints"], False)

    def test_create_with_all_options(self):
        org_id = "o1"
        payload = {
            "id": 2693833,
            "name": "full-app",
            "description": "A full test app",
            "url": "https://example.com",
            "grantTypes": ["client_credentials", "authorization_code"],
            "redirectUri": ["https://example.com/callback"],
            "clientId": "def456",
            "clientSecret": "secret789",
        }
        resp = make_response(
            status=200,
            json_body=payload,
            url=f"{BASE}/apiplatform/repository/v2/organizations/{org_id}/applications",
        )
        session = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=session, retries=0)

        result = Applications(http).create(
            org_id,
            "full-app",
            description="A full test app",
            url="https://example.com",
            grant_types=["client_credentials", "authorization_code"],
            redirect_uris=["https://example.com/callback"],
            api_endpoints=True,
        )

        self.assertEqual(result["id"], 2693833)
        self.assertEqual(result["description"], "A full test app")
        # Verify request payload
        self.assertEqual(session.calls[0]["json"]["name"], "full-app")
        self.assertEqual(session.calls[0]["json"]["description"], "A full test app")
        self.assertEqual(session.calls[0]["json"]["url"], "https://example.com")
        self.assertEqual(
            session.calls[0]["json"]["grantTypes"],
            ["client_credentials", "authorization_code"],
        )
        self.assertEqual(
            session.calls[0]["json"]["redirectUri"], ["https://example.com/callback"]
        )
        self.assertEqual(session.calls[0]["json"]["apiEndpoints"], True)

    def test_update_basic(self):
        org_id = "o1"
        app_id = 2693832
        payload = {
            "id": app_id,
            "name": "updated-app",
            "clientId": "abc123",
        }
        resp = make_response(
            status=200,
            json_body=payload,
            url=f"{BASE}/apiplatform/repository/v2/organizations/{org_id}/applications/{app_id}",
        )
        session = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=session, retries=0)

        result = Applications(http).update(org_id, app_id, "updated-app")

        self.assertEqual(result["id"], app_id)
        self.assertEqual(result["name"], "updated-app")
        # Verify PUT method used
        self.assertEqual(session.calls[0]["method"], "PUT")
        self.assertEqual(session.calls[0]["json"]["name"], "updated-app")

    def test_update_with_all_options(self):
        org_id = "o1"
        app_id = 2693832
        payload = {
            "id": app_id,
            "name": "updated-app",
            "description": "Updated description",
            "url": "https://updated.example.com",
            "grantTypes": ["authorization_code"],
            "redirectUri": ["https://updated.example.com/callback"],
        }
        resp = make_response(
            status=200,
            json_body=payload,
            url=f"{BASE}/apiplatform/repository/v2/organizations/{org_id}/applications/{app_id}",
        )
        session = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=session, retries=0)

        result = Applications(http).update(
            org_id,
            app_id,
            "updated-app",
            description="Updated description",
            url="https://updated.example.com",
            grant_types=["authorization_code"],
            redirect_uris=["https://updated.example.com/callback"],
        )

        self.assertEqual(result["id"], app_id)
        self.assertEqual(result["description"], "Updated description")
        # Verify PUT method and payload
        self.assertEqual(session.calls[0]["method"], "PUT")
        self.assertEqual(session.calls[0]["json"]["name"], "updated-app")
        self.assertEqual(session.calls[0]["json"]["description"], "Updated description")
        self.assertEqual(session.calls[0]["json"]["url"], "https://updated.example.com")
        self.assertEqual(session.calls[0]["json"]["grantTypes"], ["authorization_code"])
        self.assertEqual(
            session.calls[0]["json"]["redirectUri"],
            ["https://updated.example.com/callback"],
        )

    def test_delete(self):
        org_id = "o1"
        app_id = 2693832
        resp = make_response(
            status=204,
            json_body=None,
            url=f"{BASE}/apiplatform/repository/v2/organizations/{org_id}/applications/{app_id}",
        )
        session = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=session, retries=0)

        # Should not raise
        Applications(http).delete(org_id, app_id)

        self.assertEqual(session.calls[0]["method"], "DELETE")
        self.assertIn(f"/applications/{app_id}", session.calls[0]["url"])


if __name__ == "__main__":
    unittest.main()
