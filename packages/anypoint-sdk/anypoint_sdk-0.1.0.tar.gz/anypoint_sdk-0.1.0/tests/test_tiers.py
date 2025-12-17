# tests/test_tiers.py
import unittest

from anypoint_sdk._http import HttpClient
from anypoint_sdk.resources.tiers import Tiers
from tests.fakes import FakeSession
from tests.helpers import make_response

BASE = "https://api.test.local"


class TiersTests(unittest.TestCase):
    def test_list_api_tiers_normalises_and_dedupes(self):
        org_id = "o1"
        env_id = "e1"
        api_id = 20473240
        payload = {
            "total": 2,
            "tiers": [
                {
                    "id": 2247207,
                    "name": "gold",
                    "description": "gold ties",
                    "limits": [
                        {
                            "maximumRequests": 100,
                            "timePeriodInMilliseconds": 1000,
                            "visible": True,
                        }
                    ],
                    "status": "ACTIVE",
                    "autoApprove": False,
                    "applicationCount": 2,
                },
                # duplicate to prove dedupe
                {"id": 2247207, "name": "gold"},
            ],
        }
        resp = make_response(
            status=200,
            json_body=payload,
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/apis/{api_id}/tiers",
        )
        http = HttpClient(base_url=BASE, session=FakeSession([resp]), retries=0)

        out = Tiers(http).list_api_tiers(org_id, env_id, api_id)

        self.assertEqual(len(out), 1)
        t = out[0]
        self.assertEqual(t["id"], 2247207)
        self.assertEqual(t["name"], "gold")
        self.assertEqual(t["status"], "ACTIVE")
        self.assertIsInstance(t["limits"], list)
        self.assertEqual(t["applicationCount"], 2)

    def test_list_api_tiers_handles_missing_or_non_list(self):
        org_id = "o1"
        env_id = "e1"
        api_id = 1
        # No 'tiers' key
        resp1 = make_response(
            status=200,
            json_body={"total": 0},
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/apis/{api_id}/tiers",
        )
        http1 = HttpClient(base_url=BASE, session=FakeSession([resp1]), retries=0)
        out1 = Tiers(http1).list_api_tiers(org_id, env_id, api_id)
        self.assertEqual(out1, [])

        # 'tiers' not a list, but 'values' is present
        resp2 = make_response(
            status=200,
            json_body={"values": [{"id": 1, "name": "bronze"}]},
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/apis/{api_id}/tiers",
        )
        http2 = HttpClient(base_url=BASE, session=FakeSession([resp2]), retries=0)
        out2 = Tiers(http2).list_api_tiers(org_id, env_id, api_id)
        self.assertEqual(out2[0]["name"], "bronze")

        # 'tiers' and 'values' both wrong types
        resp3 = make_response(
            status=200,
            json_body={"tiers": {"unexpected": True}, "values": "oops"},
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/apis/{api_id}/tiers",
        )
        http3 = HttpClient(base_url=BASE, session=FakeSession([resp3]), retries=0)
        out3 = Tiers(http3).list_api_tiers(org_id, env_id, api_id)
        self.assertEqual(out3, [])

    def test_list_api_tiers_ignores_non_dict_entries(self):
        org_id = "o1"
        env_id = "e1"
        api_id = 1
        payload = {"tiers": ["bad", 123, None]}
        resp = make_response(
            status=200,
            json_body=payload,
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/apis/{api_id}/tiers",
        )
        http = HttpClient(base_url=BASE, session=FakeSession([resp]), retries=0)

        out = Tiers(http).list_api_tiers(org_id, env_id, api_id)
        self.assertEqual(out, [])

    def test_create_tier_basic(self):
        org_id = "o1"
        env_id = "e1"
        api_id = 20612480
        limits = [{"maximumRequests": 100, "timePeriodInMilliseconds": 60000}]
        payload = {
            "id": 2331798,
            "name": "gold",
            "status": "ACTIVE",
            "autoApprove": True,
            "limits": limits,
            "apiId": api_id,
        }
        resp = make_response(
            status=200,
            json_body=payload,
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/apis/{api_id}/tiers",
        )
        session = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=session, retries=0)

        result = Tiers(http).create_tier(
            org_id, env_id, api_id, "gold", limits, auto_approve=True
        )

        self.assertEqual(result["id"], 2331798)
        self.assertEqual(result["name"], "gold")
        self.assertEqual(result["status"], "ACTIVE")
        # Verify request payload
        self.assertEqual(session.calls[0]["json"]["name"], "gold")
        self.assertEqual(session.calls[0]["json"]["status"], "ACTIVE")
        self.assertEqual(session.calls[0]["json"]["autoApprove"], True)
        self.assertEqual(session.calls[0]["json"]["limits"], limits)

    def test_create_tier_with_description(self):
        org_id = "o1"
        env_id = "e1"
        api_id = 20612480
        limits = [{"maximumRequests": 50, "timePeriodInMilliseconds": 60000}]
        payload = {
            "id": 2331799,
            "name": "silver",
            "description": "Silver tier",
            "status": "ACTIVE",
            "autoApprove": False,
            "limits": limits,
        }
        resp = make_response(
            status=200,
            json_body=payload,
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/apis/{api_id}/tiers",
        )
        session = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=session, retries=0)

        result = Tiers(http).create_tier(
            org_id, env_id, api_id, "silver", limits, description="Silver tier"
        )

        self.assertEqual(result["id"], 2331799)
        self.assertEqual(result["description"], "Silver tier")
        # Verify description in request payload
        self.assertEqual(session.calls[0]["json"]["description"], "Silver tier")

    def test_update_tier(self):
        org_id = "o1"
        env_id = "e1"
        api_id = 20612480
        tier_id = 2331798
        limits = [{"maximumRequests": 200, "timePeriodInMilliseconds": 60000}]
        payload = {
            "id": tier_id,
            "name": "gold",
            "description": "Updated gold tier",
            "status": "ACTIVE",
            "autoApprove": True,
            "limits": limits,
        }
        resp = make_response(
            status=200,
            json_body=payload,
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/apis/{api_id}/tiers/{tier_id}",
        )
        session = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=session, retries=0)

        result = Tiers(http).update_tier(
            org_id,
            env_id,
            api_id,
            tier_id,
            "gold",
            limits,
            description="Updated gold tier",
            auto_approve=True,
        )

        self.assertEqual(result["id"], tier_id)
        self.assertEqual(result["description"], "Updated gold tier")
        # Verify PUT method used
        self.assertEqual(session.calls[0]["method"], "PUT")
        self.assertEqual(session.calls[0]["json"]["name"], "gold")
        self.assertEqual(session.calls[0]["json"]["limits"], limits)

    def test_delete_tier(self):
        org_id = "o1"
        env_id = "e1"
        api_id = 20612480
        tier_id = 2331798
        resp = make_response(
            status=204,
            json_body=None,
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/apis/{api_id}/tiers/{tier_id}",
        )
        session = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=session, retries=0)

        # Should not raise
        Tiers(http).delete_tier(org_id, env_id, api_id, tier_id)

        self.assertEqual(session.calls[0]["method"], "DELETE")
        self.assertIn(f"/tiers/{tier_id}", session.calls[0]["url"])


if __name__ == "__main__":
    unittest.main()
