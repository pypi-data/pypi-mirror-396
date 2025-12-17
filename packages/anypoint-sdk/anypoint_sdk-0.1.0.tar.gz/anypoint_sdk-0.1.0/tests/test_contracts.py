# tests/test_contracts.py
import unittest

from anypoint_sdk._http import HttpClient
from anypoint_sdk.resources.contracts import Contracts
from tests.fakes import FakeSession
from tests.helpers import make_response

BASE = "https://api.test.local"


class ContractsTests(unittest.TestCase):
    def test_list_api_contracts_normalises_and_dedupes(self):
        org_id = "o1"
        env_id = "e1"
        api_id = 20473240
        payload = {
            "total": 2,
            "contracts": [
                {
                    "id": 7534804,
                    "status": "APPROVED",
                    "approvedDate": "2025-08-14T17:17:30.341Z",
                    "applicationId": 2693438,
                    "application": {"id": 2693438, "name": "my-client-app-2"},
                    "tierId": 2247207,
                    "tier": {
                        "id": 2247207,
                        "name": "gold",
                        "limits": [
                            {
                                "maximumRequests": 100,
                                "timePeriodInMilliseconds": 1000,
                                "visible": True,
                            }
                        ],
                    },
                    "apiId": api_id,
                    "condition": "APPLIED",
                },
                # duplicate id to prove dedupe
                {
                    "id": 7534804,
                    "status": "APPROVED",
                    "application": {"id": 2693438, "name": "my-client-app-2"},
                    "tier": {"id": 2247207, "name": "gold"},
                    "apiId": api_id,
                },
            ],
        }
        resp = make_response(
            status=200,
            json_body=payload,
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/apis/{api_id}/contracts",
        )
        http = HttpClient(base_url=BASE, session=FakeSession([resp]), retries=0)

        out = Contracts(http).list_api_contracts(org_id, env_id, api_id)

        self.assertEqual(len(out), 1)
        c = out[0]
        self.assertEqual(c["id"], 7534804)
        self.assertEqual(c["status"], "APPROVED")
        self.assertEqual(c["applicationId"], 2693438)
        self.assertEqual(c["applicationName"], "my-client-app-2")
        self.assertEqual(c["tierId"], 2247207)
        self.assertEqual(c["tierName"], "gold")
        self.assertIsInstance(c["tierLimits"], list)

    def test_list_api_contracts_handles_missing_or_non_list(self):
        org_id = "o1"
        env_id = "e1"
        api_id = 1
        # No 'contracts' key
        resp1 = make_response(
            status=200,
            json_body={"total": 0},
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/apis/{api_id}/contracts",
        )
        http1 = HttpClient(base_url=BASE, session=FakeSession([resp1]), retries=0)
        out1 = Contracts(http1).list_api_contracts(org_id, env_id, api_id)
        self.assertEqual(out1, [])

        # 'contracts' is not a list
        resp2 = make_response(
            status=200,
            json_body={"contracts": {"unexpected": True}},
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/apis/{api_id}/contracts",
        )
        http2 = HttpClient(base_url=BASE, session=FakeSession([resp2]), retries=0)
        out2 = Contracts(http2).list_api_contracts(org_id, env_id, api_id)
        self.assertEqual(out2, [])

    def test_list_api_contracts_ignores_non_dict_entries(self):
        org_id = "o1"
        env_id = "e1"
        api_id = 1
        payload = {"contracts": ["bad", 123, None]}
        resp = make_response(
            status=200,
            json_body=payload,
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/apis/{api_id}/contracts",
        )
        http = HttpClient(base_url=BASE, session=FakeSession([resp]), retries=0)

        out = Contracts(http).list_api_contracts(org_id, env_id, api_id)
        self.assertEqual(out, [])

    def test_group_contracts_default_limits_wrong_type_limits_by_api_list(self):
        org_id = "o1"
        env_id = "e1"
        gid = 1
        api_id = 42
        payload = {
            "contracts": [
                {
                    "id": 1001,
                    "apiId": api_id,
                    "tier": {
                        "id": 2001,
                        "name": "tier-a",
                        "defaultLimits": "not-a-list",  # forces the false branch at line 154
                        "limitsByApi": [
                            {"apiId": api_id, "limits": [{"maximumRequests": 5}]},
                            "bad",  # non-dict filtered out
                        ],
                    },
                }
            ]
        }
        resp = make_response(
            status=200,
            json_body=payload,
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/groupInstances/{gid}/contracts",
        )
        http = HttpClient(base_url=BASE, session=FakeSession([resp]), retries=0)

        out = Contracts(http).list_group_contracts(org_id, env_id, gid)

        self.assertEqual(len(out), 1)
        row = out[0]
        # defaultLimits was wrong type, remains None
        self.assertIsNone(row["tierDefaultLimits"])
        # limitsByApi was a list, only dict entries remain
        self.assertIsInstance(row["tierLimitsByApi"], list)
        self.assertEqual(len(row["tierLimitsByApi"]), 1)
        self.assertEqual(row["tierLimitsByApi"][0]["apiId"], api_id)

    def test_group_contracts_default_limits_list_limits_by_api_wrong_type(self):
        org_id = "o1"
        env_id = "e1"
        gid = 1
        payload = {
            "contracts": [
                {
                    "id": 1002,
                    "tier": {
                        "id": 2002,
                        "name": "tier-b",
                        "defaultLimits": [  # true branch at line 154
                            {"maximumRequests": 50, "timePeriodInMilliseconds": 10000}
                        ],
                        "limitsByApi": {
                            "unexpected": True
                        },  # forces false branch at line 158
                    },
                }
            ]
        }
        resp = make_response(
            status=200,
            json_body=payload,
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/groupInstances/{gid}/contracts",
        )
        http = HttpClient(base_url=BASE, session=FakeSession([resp]), retries=0)

        out = Contracts(http).list_group_contracts(org_id, env_id, gid)

        self.assertEqual(len(out), 1)
        row = out[0]
        # defaultLimits kept
        self.assertIsInstance(row["tierDefaultLimits"], list)
        self.assertGreaterEqual(len(row["tierDefaultLimits"]), 1)
        # limitsByApi wrong type, remains None
        self.assertIsNone(row["tierLimitsByApi"])

    def test_create_contract_basic(self):
        org_id = "o1"
        env_id = "e1"
        api_id = 20612480
        app_id = 2790867
        payload = {
            "id": 7969530,
            "status": "APPROVED",
            "applicationId": app_id,
            "apiId": api_id,
            "tierId": None,
        }
        resp = make_response(
            status=200,
            json_body=payload,
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/apis/{api_id}/contracts",
        )
        session = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=session, retries=0)

        result = Contracts(http).create_contract(org_id, env_id, api_id, app_id)

        self.assertEqual(result["id"], 7969530)
        self.assertEqual(result["status"], "APPROVED")
        self.assertEqual(result["applicationId"], app_id)
        # Verify request payload
        self.assertEqual(session.calls[0]["json"], {"applicationId": app_id})

    def test_create_contract_with_tier(self):
        org_id = "o1"
        env_id = "e1"
        api_id = 20612480
        app_id = 2790867
        tier_id = 12345
        payload = {
            "id": 7969531,
            "status": "APPROVED",
            "applicationId": app_id,
            "apiId": api_id,
            "tierId": tier_id,
        }
        resp = make_response(
            status=200,
            json_body=payload,
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/apis/{api_id}/contracts",
        )
        session = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=session, retries=0)

        result = Contracts(http).create_contract(
            org_id, env_id, api_id, app_id, tier_id=tier_id
        )

        self.assertEqual(result["id"], 7969531)
        self.assertEqual(result["tierId"], tier_id)
        # Verify request payload includes tierId
        self.assertEqual(
            session.calls[0]["json"], {"applicationId": app_id, "tierId": tier_id}
        )

    def test_revoke_contract(self):
        org_id = "o1"
        env_id = "e1"
        api_id = 20612480
        contract_id = 7969530
        payload = {
            "id": contract_id,
            "status": "REVOKED",
            "revokedDate": "2025-12-14T14:45:58.038Z",
        }
        resp = make_response(
            status=200,
            json_body=payload,
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/apis/{api_id}/contracts/{contract_id}",
        )
        session = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=session, retries=0)

        result = Contracts(http).revoke_contract(org_id, env_id, api_id, contract_id)

        self.assertEqual(result["id"], contract_id)
        self.assertEqual(result["status"], "REVOKED")
        # Verify request payload
        self.assertEqual(session.calls[0]["json"], {"status": "REVOKED"})
        self.assertEqual(session.calls[0]["method"], "PATCH")

    def test_delete_contract(self):
        org_id = "o1"
        env_id = "e1"
        api_id = 20612480
        contract_id = 7969530
        resp = make_response(
            status=204,
            json_body=None,
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/apis/{api_id}/contracts/{contract_id}",
        )
        session = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=session, retries=0)

        # Should not raise
        Contracts(http).delete_contract(org_id, env_id, api_id, contract_id)

        self.assertEqual(session.calls[0]["method"], "DELETE")
        self.assertIn(f"/contracts/{contract_id}", session.calls[0]["url"])


if __name__ == "__main__":
    unittest.main()
