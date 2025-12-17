# tests/test_apis.py

import unittest

from anypoint_sdk._http import HttpClient
from anypoint_sdk.resources.apis import APIs
from tests.fakes import FakeSession
from tests.helpers import make_response

BASE = "https://api.test.local"


class APIsTests(unittest.TestCase):
    def test_list_instances_flattens_assets_and_dedupes(self):
        org_id = "o1"
        env_id = "e1"
        payload = {
            "total": 2,
            "assets": [
                {
                    "exchangeAssetName": "api-1",
                    "groupId": "g1",
                    "assetId": "api-1",
                    "apis": [
                        {
                            "id": 101,
                            "groupId": "g1",
                            "assetId": "api-1",
                            "assetVersion": "1.0.0",
                            "productVersion": "v1",
                            "environmentId": env_id,
                            "instanceLabel": None,
                            "status": "active",
                            "technology": "mule4",
                            "activeContractsCount": 3,
                        }
                    ],
                },
                {
                    "exchangeAssetName": "api-2",
                    "groupId": "g1",
                    "assetId": "api-2",
                    "apis": [
                        {
                            "id": 102,
                            "groupId": "g1",
                            "assetId": "api-2",
                            "assetVersion": "2.0.0",
                            "productVersion": "v2",
                            "environmentId": env_id,
                            "instanceLabel": "sapi-proxy-1",
                            "status": "active",
                            "technology": "mule4",
                            "activeContractsCount": 2,
                        },
                        {
                            "id": 102,
                            "groupId": "g1",
                            "assetId": "api-2",
                        },  # duplicate to prove dedupe
                    ],
                },
            ],
        }
        resp = make_response(
            status=200,
            json_body=payload,
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/apis",
        )
        http = HttpClient(base_url=BASE, session=FakeSession([resp]), retries=0)

        apis = APIs(http).list_instances(org_id, env_id)

        self.assertEqual(len(apis), 2)
        ids = {a["id"] for a in apis}
        self.assertSetEqual(ids, {101, 102})
        a101 = next(a for a in apis if a["id"] == 101)
        self.assertEqual(a101["assetVersion"], "1.0.0")
        self.assertEqual(a101["exchangeAssetName"], "api-1")

    def test_list_instances_handles_missing_assets_and_non_dicts(self):
        org_id = "o1"
        env_id = "e1"
        payload = {"total": 0, "assets": ["not-a-dict"]}
        resp = make_response(
            status=200,
            json_body=payload,
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/apis",
        )
        http = HttpClient(base_url=BASE, session=FakeSession([resp]), retries=0)

        apis = APIs(http).list_instances(org_id, env_id)

        self.assertEqual(apis, [])

    def test_get_instance_returns_detail(self):
        org_id = "o1"
        env_id = "e1"
        api_id = 123
        detail = {"id": api_id, "assetId": "api-1", "productVersion": "v1"}
        resp = make_response(
            status=200,
            json_body=detail,
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/apis/{api_id}",
        )
        http = HttpClient(base_url=BASE, session=FakeSession([resp]), retries=0)

        got = APIs(http).get_instance(org_id, env_id, api_id)

        self.assertEqual(got["id"], api_id)

    def test_list_instances_ignores_non_dict_items_in_apis(self):
        org_id = "o1"
        env_id = "e1"
        payload = {
            "total": 1,
            "assets": [
                {
                    "exchangeAssetName": "api-odd",
                    "groupId": "g1",
                    "assetId": "api-odd",
                    "apis": ["not-a-dict", 123, None],  # exercise the false branch
                }
            ],
        }
        resp = make_response(
            status=200,
            json_body=payload,
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/apis",
        )
        http = HttpClient(base_url=BASE, session=FakeSession([resp]), retries=0)

        apis = APIs(http).list_instances(org_id, env_id)

        self.assertEqual(apis, [])  # all items ignored

    def test_get_instance_empty_body_returns_empty_dict(self):
        org_id = "o1"
        env_id = "e1"
        api_id = 999

        # Empty body triggers _Response.json() -> None, so get_instance returns {}
        resp = make_response(
            status=200,
            text="",
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/apis/{api_id}",
        )
        http = HttpClient(base_url=BASE, session=FakeSession([resp]), retries=0)

        got = APIs(http).get_instance(org_id, env_id, api_id)
        self.assertEqual(got, {})

    def test_list_instances_assets_missing_triggers_empty_fallback(self):
        org_id = "o1"
        env_id = "e1"
        payload = {"total": 0}  # no "assets" key, so assets is None, not a list
        resp = make_response(
            status=200,
            json_body=payload,
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/apis",
        )
        http = HttpClient(base_url=BASE, session=FakeSession([resp]), retries=0)

        out = APIs(http).list_instances(org_id, env_id)

        self.assertEqual(out, [])  # falls back to empty list


if __name__ == "__main__":
    unittest.main()
