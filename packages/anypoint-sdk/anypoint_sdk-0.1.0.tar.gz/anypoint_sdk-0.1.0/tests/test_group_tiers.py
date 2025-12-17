# tests/test_group_tiers.py
import unittest

from anypoint_sdk._http import HttpClient
from anypoint_sdk.resources.tiers import Tiers
from tests.fakes import FakeSession
from tests.helpers import make_response

BASE = "https://api.test.local"


class GroupTiersTests(unittest.TestCase):
    def test_list_group_tiers_normalises_dedupes_and_adds_group_fields(self):
        org_id = "o1"
        env_id = "e1"
        gid = 368690
        payload = {
            "total": 2,
            "tiers": [
                {
                    "id": 2248233,
                    "name": "Bronze",
                    "description": "Bronze Tier",
                    "limitsByApi": [
                        {
                            "apiId": 20473240,
                            "limits": [
                                {
                                    "maximumRequests": 10,
                                    "timePeriodInMilliseconds": 50000,
                                    "visible": True,
                                }
                            ],
                        }
                    ],
                    "status": "ACTIVE",
                    "autoApprove": True,
                    "applicationCount": 0,
                },
                {
                    "id": 2247208,
                    "name": "silver",
                    "description": "silver tier",
                    "defaultLimits": [
                        {
                            "maximumRequests": 50,
                            "timePeriodInMilliseconds": 10000,
                            "visible": True,
                        }
                    ],
                    "status": "ACTIVE",
                    "autoApprove": True,
                    "applicationCount": 1,
                },
                # duplicate to prove de-dupe
                {"id": 2247208, "name": "silver"},
            ],
        }
        resp = make_response(
            status=200,
            json_body=payload,
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/groupInstances/{gid}/tiers",
        )
        http = HttpClient(base_url=BASE, session=FakeSession([resp]), retries=0)

        out = Tiers(http).list_group_tiers(org_id, env_id, gid)

        # Should be two unique tiers
        self.assertEqual(len(out), 2)
        ids = {t["id"] for t in out}
        self.assertSetEqual(ids, {2248233, 2247208})
        slvr = next(t for t in out if t["id"] == 2247208)
        self.assertIsInstance(slvr["defaultLimits"], list)
        brnz = next(t for t in out if t["id"] == 2248233)
        self.assertIsInstance(brnz["limitsByApi"], list)

    def test_list_group_tiers_handles_missing_or_non_list(self):
        org_id = "o1"
        env_id = "e1"
        gid = 1
        # No tiers key
        resp1 = make_response(
            status=200,
            json_body={"total": 0},
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/groupInstances/{gid}/tiers",
        )
        http1 = HttpClient(base_url=BASE, session=FakeSession([resp1]), retries=0)
        out1 = Tiers(http1).list_group_tiers(org_id, env_id, gid)
        self.assertEqual(out1, [])

        # Wrong type for tiers, but values present
        resp2 = make_response(
            status=200,
            json_body={"values": [{"id": 1, "name": "bronze"}]},
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/groupInstances/{gid}/tiers",
        )
        http2 = HttpClient(base_url=BASE, session=FakeSession([resp2]), retries=0)
        out2 = Tiers(http2).list_group_tiers(org_id, env_id, gid)
        self.assertEqual(out2[0]["name"], "bronze")

        # Both wrong types
        resp3 = make_response(
            status=200,
            json_body={"tiers": {"unexpected": True}, "values": "oops"},
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/groupInstances/{gid}/tiers",
        )
        http3 = HttpClient(base_url=BASE, session=FakeSession([resp3]), retries=0)
        out3 = Tiers(http3).list_group_tiers(org_id, env_id, gid)
        self.assertEqual(out3, [])

    def test_list_group_tiers_ignores_non_dict_entries(self):
        org_id = "o1"
        env_id = "e1"
        gid = 1
        resp = make_response(
            status=200,
            json_body={"tiers": ["bad", 123, None]},
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/groupInstances/{gid}/tiers",
        )
        http = HttpClient(base_url=BASE, session=FakeSession([resp]), retries=0)

        out = Tiers(http).list_group_tiers(org_id, env_id, gid)
        self.assertEqual(out, [])


if __name__ == "__main__":
    unittest.main()
