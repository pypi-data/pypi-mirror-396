# tests/test_policies.py

import unittest

from anypoint_sdk._http import HttpClient
from anypoint_sdk.resources.policies import Policies
from tests.fakes import FakeSession
from tests.helpers import make_response

BASE = "https://api.test.local"


class PoliciesTests(unittest.TestCase):
    def test_list_api_policies_normalises_and_dedupes(self):
        org_id = "o1"
        env_id = "e1"
        api_id = 20473240
        payload = {
            "policies": [
                {
                    "policyTemplateId": "348742",
                    "order": 1,
                    "type": "system",
                    "policyId": 7038442,
                    "implementationAsset": {
                        "assetId": "rate-limiting-sla-based-mule",
                        "groupId": "68ef9520-24e9-4cf2-b2f5-620025690913",
                        "version": "1.3.0",
                        "technology": "mule4",
                    },
                    "configuration": {"exposeHeaders": True},
                },
                # duplicate policyId to prove dedupe
                {
                    "policyTemplateId": "348742",
                    "order": 1,
                    "type": "system",
                    "policyId": 7038442,
                },
            ]
        }
        resp = make_response(
            status=200,
            json_body=payload,
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/apis/{api_id}/policies",
        )
        http = HttpClient(base_url=BASE, session=FakeSession([resp]), retries=0)

        out = Policies(http).list_api_policies(org_id, env_id, api_id)

        self.assertEqual(len(out), 1)
        p = out[0]
        self.assertEqual(p["policyId"], 7038442)
        self.assertEqual(p["type"], "system")
        self.assertEqual(p["order"], 1)
        self.assertIn("implementationAsset", p)

    def test_list_api_policies_handles_missing_or_non_list(self):
        org_id = "o1"
        env_id = "e1"
        api_id = 1
        # No 'policies' key
        resp = make_response(
            status=200,
            json_body={"tiers": {"values": []}},
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/apis/{api_id}/policies",
        )
        http = HttpClient(base_url=BASE, session=FakeSession([resp]), retries=0)

        out = Policies(http).list_api_policies(org_id, env_id, api_id)
        self.assertEqual(out, [])

    def test_list_api_policies_ignores_non_dict_entries(self):
        org_id = "o1"
        env_id = "e1"
        api_id = 1
        resp = make_response(
            status=200,
            json_body={"policies": ["bad", 123, None]},
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/apis/{api_id}/policies",
        )
        http = HttpClient(base_url=BASE, session=FakeSession([resp]), retries=0)

        out = Policies(http).list_api_policies(org_id, env_id, api_id)
        self.assertEqual(out, [])

    def test_apply_api_policy_posts_json(self):
        org_id = "o1"
        env_id = "e1"
        api_id = 123
        policy_data = {
            "policyTemplateId": "rate-limiting",
            "configuration": {"rateLimit": 100, "period": "minute"},
            "order": 1,
        }
        resp = make_response(
            status=201,
            json_body={"policyId": 999, **policy_data},
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/apis/{api_id}/policies",
            method="POST",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        result = Policies(http).apply_api_policy(org_id, env_id, api_id, policy_data)

        self.assertEqual(result["policyId"], 999)
        self.assertEqual(fake.calls[0]["method"], "POST")
        self.assertEqual(
            fake.calls[0]["url"],
            f"{BASE}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/apis/{api_id}/policies",
        )
        self.assertEqual(fake.calls[0]["json"], policy_data)
        self.assertEqual(fake.calls[0]["headers"]["Content-Type"], "application/json")

    def test_apply_api_policy_template_constructs_payload(self):
        org_id = "o1"
        env_id = "e1"
        api_id = 123
        template_id = "rate-limiting"
        config = {"rateLimit": 100, "period": "minute"}

        resp = make_response(
            status=201,
            json_body={
                "policyId": 999,
                "policyTemplateId": template_id,
                "configuration": config,
            },
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/apis/{api_id}/policies",
            method="POST",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        result = Policies(http).apply_api_policy_template(
            org_id=org_id,
            env_id=env_id,
            api_id=api_id,
            policy_template_id=template_id,
            configuration=config,
            order=1,
            disabled=False,
        )

        self.assertEqual(result["policyId"], 999)
        sent_payload = fake.calls[0]["json"]
        self.assertEqual(sent_payload["policyTemplateId"], template_id)
        self.assertEqual(sent_payload["configurationData"], config)
        self.assertEqual(sent_payload["order"], 1)
        self.assertFalse(sent_payload["disabled"])
        # Verify default MuleSoft policy group ID and asset info are included
        self.assertEqual(
            sent_payload["groupId"], "68ef9520-24e9-4cf2-b2f5-620025690913"
        )
        self.assertEqual(sent_payload["assetId"], template_id)
        self.assertEqual(sent_payload["assetVersion"], "1.4.1")

    def test_update_api_policy_sends_patch(self):
        org_id = "o1"
        env_id = "e1"
        api_id = 123
        policy_id = 999
        update_data = {"configuration": {"rateLimit": 200, "period": "minute"}}

        resp = make_response(
            status=200,
            json_body={"policyId": policy_id, **update_data},
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/apis/{api_id}/policies/{policy_id}",
            method="PATCH",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        result = Policies(http).update_api_policy(
            org_id, env_id, api_id, policy_id, update_data
        )

        self.assertEqual(result["policyId"], policy_id)
        self.assertEqual(fake.calls[0]["method"], "PATCH")
        self.assertEqual(
            fake.calls[0]["url"],
            f"{BASE}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/apis/{api_id}/policies/{policy_id}",
        )
        self.assertEqual(fake.calls[0]["json"], update_data)

    def test_delete_api_policy_sends_delete(self):
        org_id = "o1"
        env_id = "e1"
        api_id = 123
        policy_id = 999

        resp = make_response(
            status=204,
            text="",
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/apis/{api_id}/policies/{policy_id}",
            method="DELETE",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        # Should not raise
        Policies(http).delete_api_policy(org_id, env_id, api_id, policy_id)

        self.assertEqual(fake.calls[0]["method"], "DELETE")
        self.assertEqual(
            fake.calls[0]["url"],
            f"{BASE}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/apis/{api_id}/policies/{policy_id}",
        )

    def test_apply_api_policy_template_with_custom_group_id(self):
        org_id = "o1"
        env_id = "e1"
        api_id = 123
        template_id = "custom-policy"
        custom_group_id = "custom-group-12345"

        resp = make_response(
            status=201,
            json_body={"policyId": 888},
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/apis/{api_id}/policies",
            method="POST",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        Policies(http).apply_api_policy_template(
            org_id=org_id,
            env_id=env_id,
            api_id=api_id,
            policy_template_id=template_id,
            group_id=custom_group_id,
        )

        sent_payload = fake.calls[0]["json"]
        self.assertEqual(sent_payload["groupId"], custom_group_id)

    def test_apply_api_policy_template_with_custom_asset_id(self):
        org_id = "o1"
        env_id = "e1"
        api_id = 123
        template_id = "rate-limiting"
        custom_asset_id = "my-custom-asset"

        resp = make_response(
            status=201,
            json_body={"policyId": 888},
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/apis/{api_id}/policies",
            method="POST",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        Policies(http).apply_api_policy_template(
            org_id=org_id,
            env_id=env_id,
            api_id=api_id,
            policy_template_id=template_id,
            asset_id=custom_asset_id,
        )

        sent_payload = fake.calls[0]["json"]
        self.assertEqual(sent_payload["assetId"], custom_asset_id)

    def test_apply_api_policy_template_with_custom_asset_version(self):
        org_id = "o1"
        env_id = "e1"
        api_id = 123
        template_id = "rate-limiting"
        custom_version = "2.0.0"

        resp = make_response(
            status=201,
            json_body={"policyId": 888},
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/apis/{api_id}/policies",
            method="POST",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        Policies(http).apply_api_policy_template(
            org_id=org_id,
            env_id=env_id,
            api_id=api_id,
            policy_template_id=template_id,
            asset_version=custom_version,
        )

        sent_payload = fake.calls[0]["json"]
        self.assertEqual(sent_payload["assetVersion"], custom_version)

    def test_apply_api_policy_template_with_pointcut_data(self):
        org_id = "o1"
        env_id = "e1"
        api_id = 123
        template_id = "rate-limiting"
        pointcut = {"methodRegex": "GET|POST", "uriTemplateRegex": "/api/.*"}

        resp = make_response(
            status=201,
            json_body={"policyId": 888},
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/apis/{api_id}/policies",
            method="POST",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        Policies(http).apply_api_policy_template(
            org_id=org_id,
            env_id=env_id,
            api_id=api_id,
            policy_template_id=template_id,
            pointcut_data=pointcut,
        )

        sent_payload = fake.calls[0]["json"]
        self.assertEqual(sent_payload["pointcutData"], pointcut)

    def test_apply_api_policy_template_with_all_custom_options(self):
        org_id = "o1"
        env_id = "e1"
        api_id = 123
        template_id = "custom-policy"
        config = {"key": "value"}
        pointcut = {"methodRegex": ".*"}

        resp = make_response(
            status=201,
            json_body={"policyId": 888},
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/apis/{api_id}/policies",
            method="POST",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        Policies(http).apply_api_policy_template(
            org_id=org_id,
            env_id=env_id,
            api_id=api_id,
            policy_template_id=template_id,
            configuration=config,
            disabled=True,
            order=5,
            pointcut_data=pointcut,
            group_id="my-group",
            asset_id="my-asset",
            asset_version="3.0.0",
        )

        sent_payload = fake.calls[0]["json"]
        self.assertEqual(sent_payload["policyTemplateId"], template_id)
        self.assertEqual(sent_payload["groupId"], "my-group")
        self.assertEqual(sent_payload["assetId"], "my-asset")
        self.assertEqual(sent_payload["assetVersion"], "3.0.0")
        self.assertEqual(sent_payload["configurationData"], config)
        self.assertTrue(sent_payload["disabled"])
        self.assertEqual(sent_payload["order"], 5)
        self.assertEqual(sent_payload["pointcutData"], pointcut)


if __name__ == "__main__":
    unittest.main()
