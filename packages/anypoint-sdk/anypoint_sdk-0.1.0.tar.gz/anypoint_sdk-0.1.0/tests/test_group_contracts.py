# tests/test_group_contracts.py
import unittest

from anypoint_sdk._http import HttpClient
from anypoint_sdk.resources.contracts import Contracts
from tests.fakes import FakeSession
from tests.helpers import make_response

BASE = "https://api.test.local"


class GroupContractsTests(unittest.TestCase):
    def test_list_group_contracts_normalises_dedupes_and_adds_tier_fields(self):
        org_id = "o1"
        env_id = "e1"
        gid = 368690
        api_id = 20473240
        payload = {
            "total": 1,
            "contracts": [
                {
                    "id": 7535153,
                    "status": "APPROVED",
                    "approvedDate": "2025-08-14T19:12:35.196Z",
                    "applicationId": 2693549,
                    "application": {"id": 2693549, "name": "my-client-app-3"},
                    "tierId": 2247208,
                    "tier": {
                        "id": 2247208,
                        "name": "silver",
                        "defaultLimits": [
                            {
                                "maximumRequests": 50,
                                "timePeriodInMilliseconds": 10000,
                                "visible": True,
                            }
                        ],
                        "limitsByApi": [
                            {
                                "apiId": api_id,
                                "limits": [
                                    {
                                        "maximumRequests": 50,
                                        "timePeriodInMilliseconds": 10000,
                                        "visible": True,
                                    }
                                ],
                            }
                        ],
                    },
                    "apiId": api_id,
                    "condition": "GROUP",
                },
                # duplicate contract id to prove de-dupe
                {"id": 7535153, "status": "APPROVED"},
            ],
        }
        resp = make_response(
            status=200,
            json_body=payload,
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/groupInstances/{gid}/contracts",
        )
        http = HttpClient(base_url=BASE, session=FakeSession([resp]), retries=0)

        out = Contracts(http).list_group_contracts(org_id, env_id, gid)

        self.assertEqual(len(out), 1)
        c = out[0]
        self.assertEqual(c["id"], 7535153)
        self.assertEqual(c["status"], "APPROVED")
        self.assertEqual(c["applicationName"], "my-client-app-3")
        self.assertEqual(c["tierId"], 2247208)
        self.assertEqual(c["tierName"], "silver")
        self.assertIsInstance(c["tierDefaultLimits"], list)
        self.assertIsInstance(c["tierLimitsByApi"], list)

    def test_list_group_contracts_handles_missing_or_non_list(self):
        org_id = "o1"
        env_id = "e1"
        gid = 1
        resp1 = make_response(
            status=200,
            json_body={"total": 0},
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/groupInstances/{gid}/contracts",
        )
        http1 = HttpClient(base_url=BASE, session=FakeSession([resp1]), retries=0)
        out1 = Contracts(http1).list_group_contracts(org_id, env_id, gid)
        self.assertEqual(out1, [])

        resp2 = make_response(
            status=200,
            json_body={"contracts": {"unexpected": True}},
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/groupInstances/{gid}/contracts",
        )
        http2 = HttpClient(base_url=BASE, session=FakeSession([resp2]), retries=0)
        out2 = Contracts(http2).list_group_contracts(org_id, env_id, gid)
        self.assertEqual(out2, [])

    def test_list_group_contracts_ignores_non_dict_entries(self):
        org_id = "o1"
        env_id = "e1"
        gid = 1
        resp = make_response(
            status=200,
            json_body={"contracts": ["bad", 123, None]},
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/groupInstances/{gid}/contracts",
        )
        http = HttpClient(base_url=BASE, session=FakeSession([resp]), retries=0)

        out = Contracts(http).list_group_contracts(org_id, env_id, gid)
        self.assertEqual(out, [])


if __name__ == "__main__":
    unittest.main()
