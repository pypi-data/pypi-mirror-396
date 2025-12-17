# tests/test_policies_automated.py
import unittest

from anypoint_sdk._http import HttpClient, HttpError
from anypoint_sdk.resources.policies import Policies
from tests.fakes import FakeSession
from tests.helpers import make_response

BASE = "https://api.test.local"


class PoliciesAutomatedTests(unittest.TestCase):
    def test_list_environment_automated_policies_normalises_dedupes_and_filters(self):
        org_id = "o1"
        env_id = "e1"
        payload = {
            "automatedPolicies": [
                {
                    "audit": {"created": {"date": "2025-08-13T14:20:55.647Z"}},
                    "id": 129720,
                    "ruleOfApplication": {
                        "environmentId": env_id,
                        "organizationId": org_id,
                    },
                    "groupId": "68ef9520-24e9-4cf2-b2f5-620025690913",
                    "assetId": "ip-allowlist",
                    "assetVersion": "1.1.1",
                    "configurationData": {
                        "ipExpression": "#[attributes.headers['x-forwarded-for']]"
                    },
                    "order": 2,
                    "disabled": False,
                    "implementationAssets": [
                        {
                            "name": "IP Allowlist - Flex",
                            "assetId": "ip-allowlist-flex",
                            "version": "1.2.0",
                            "technology": "flexGateway",
                        },
                        {
                            "name": "IP Allowlist - Mule4",
                            "assetId": "ip-allowlist-mule",
                            "version": "1.2.0",
                            "technology": "mule4",
                        },
                        {
                            "name": "IP Allowlist - Mule4",
                            "assetId": "ip-allowlist-mule",
                            "version": "1.1.0",
                            "technology": "mule4",
                        },
                    ],
                },
                # duplicate id to prove dedupe
                {
                    "id": 129720,
                    "ruleOfApplication": {
                        "environmentId": env_id,
                        "organizationId": org_id,
                    },
                    "assetId": "ip-allowlist",
                    "assetVersion": "1.1.1",
                },
                # other env, should be filtered out
                {
                    "id": 999999,
                    "ruleOfApplication": {
                        "environmentId": "e-other",
                        "organizationId": org_id,
                    },
                    "assetId": "something-else",
                    "assetVersion": "0.1.0",
                },
            ]
        }
        resp = make_response(
            status=200,
            json_body=payload,
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/automated-policies",
        )
        http = HttpClient(base_url=BASE, session=FakeSession([resp]), retries=0)

        out = Policies(http).list_environment_automated_policies(org_id, env_id)

        self.assertEqual(len(out), 1)
        p = out[0]
        self.assertEqual(p["id"], 129720)
        self.assertEqual(p["assetId"], "ip-allowlist")
        self.assertEqual(p["assetVersion"], "1.1.1")
        self.assertEqual(p["order"], 2)
        self.assertFalse(p["disabled"])
        self.assertIsInstance(p["implementationAssets"], list)
        self.assertGreaterEqual(len(p["implementationAssets"]), 2)

    def test_list_environment_automated_policies_handles_missing_or_non_list(self):
        org_id = "o1"
        env_id = "e1"
        # no 'automatedPolicies' key
        resp1 = make_response(
            status=200,
            json_body={"total": 0},
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/automated-policies",
        )
        http1 = HttpClient(base_url=BASE, session=FakeSession([resp1]), retries=0)
        out1 = Policies(http1).list_environment_automated_policies(org_id, env_id)
        self.assertEqual(out1, [])

        # automatedPolicies is not a list
        resp2 = make_response(
            status=200,
            json_body={"automatedPolicies": {"unexpected": True}},
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/automated-policies",
        )
        http2 = HttpClient(base_url=BASE, session=FakeSession([resp2]), retries=0)
        out2 = Policies(http2).list_environment_automated_policies(org_id, env_id)
        self.assertEqual(out2, [])

    def test_list_environment_automated_policies_ignores_non_dict_entries(self):
        org_id = "o1"
        env_id = "e1"
        payload = {"automatedPolicies": ["bad", 123, None]}
        resp = make_response(
            status=200,
            json_body=payload,
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/automated-policies",
        )
        http = HttpClient(base_url=BASE, session=FakeSession([resp]), retries=0)
        out = Policies(http).list_environment_automated_policies(org_id, env_id)
        self.assertEqual(out, [])

    def test_rule_of_application_is_dict_without_env_id(self):
        org_id = "o1"
        env_id = "e1"
        payload = {
            "automatedPolicies": [
                {
                    "id": 42,
                    "ruleOfApplication": {
                        "organizationId": org_id
                    },  # dict present, no environmentId
                    "assetId": "ip-allowlist",
                    "assetVersion": "1.0.0",
                    "implementationAssets": [{"assetId": "impl", "version": "1.0.0"}],
                }
            ]
        }
        resp = make_response(
            status=200,
            json_body=payload,
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/automated-policies",
        )
        http = HttpClient(base_url=BASE, session=FakeSession([resp]), retries=0)
        out = Policies(http).list_environment_automated_policies(org_id, env_id)
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["id"], 42)

    def test_rule_of_application_non_dict_path(self):
        org_id = "o1"
        env_id = "e1"
        payload = {
            "automatedPolicies": [
                {
                    "id": 77,
                    "ruleOfApplication": "unexpected-shape",  # NOT a dict, exercises false branch
                    "assetId": "some-policy",
                    "assetVersion": "0.1.0",
                }
            ]
        }
        resp = make_response(
            status=200,
            json_body=payload,
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/automated-policies",
        )
        http = HttpClient(base_url=BASE, session=FakeSession([resp]), retries=0)
        out = Policies(http).list_environment_automated_policies(org_id, env_id)
        # Included because roa_env stays None
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["id"], 77)

    def test_create_automated_policy_success(self):
        """Test create_automated_policy sends correct payload and returns response"""
        org_id = "o1"
        env_id = "e1"
        group_id = "68ef9520-24e9-4cf2-b2f5-620025690913"
        asset_id = "rate-limiting"
        asset_version = "1.5.1"
        config_data = {
            "rateLimits": [{"timePeriodInMilliseconds": 60000, "maximumRequests": 100}]
        }

        response_body = {
            "id": 12345,
            "groupId": group_id,
            "assetId": asset_id,
            "assetVersion": asset_version,
            "configurationData": config_data,
            "order": 1,
            "disabled": False,
            "ruleOfApplication": {
                "environmentId": env_id,
                "organizationId": org_id,
            },
        }

        resp = make_response(
            status=201,
            json_body=response_body,
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/automated-policies",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        result = Policies(http).create_automated_policy(
            org_id=org_id,
            env_id=env_id,
            group_id=group_id,
            asset_id=asset_id,
            asset_version=asset_version,
            configuration_data=config_data,
            order=1,
        )

        # Verify the request
        call = fake.calls[0]
        self.assertEqual(call["method"], "POST")
        self.assertEqual(
            call["url"],
            f"{BASE}/apimanager/api/v1/organizations/{org_id}/automated-policies",
        )
        # Verify payload
        payload = call["json"]
        self.assertEqual(payload["ruleOfApplication"]["environmentId"], env_id)
        # No default range - API handles defaults
        self.assertNotIn("range", payload["ruleOfApplication"])
        self.assertEqual(payload["groupId"], group_id)
        self.assertEqual(payload["assetId"], asset_id)
        self.assertEqual(payload["assetVersion"], asset_version)
        self.assertEqual(payload["configurationData"], config_data)
        self.assertEqual(payload["order"], 1)

        # Verify response
        self.assertEqual(result["id"], 12345)
        self.assertEqual(result["assetId"], asset_id)

    def test_create_automated_policy_minimal(self):
        """Test create_automated_policy with only required fields"""
        org_id = "o1"
        env_id = "e1"
        group_id = "68ef9520-24e9-4cf2-b2f5-620025690913"
        asset_id = "cors"
        asset_version = "1.3.2"

        resp = make_response(
            status=201,
            json_body={"id": 99},
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/automated-policies",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        Policies(http).create_automated_policy(
            org_id=org_id,
            env_id=env_id,
            group_id=group_id,
            asset_id=asset_id,
            asset_version=asset_version,
        )

        call = fake.calls[0]
        payload = call["json"]
        # Required fields should be present
        self.assertIn("ruleOfApplication", payload)
        self.assertIn("groupId", payload)
        self.assertIn("assetId", payload)
        self.assertIn("assetVersion", payload)
        # No default range - API handles defaults
        self.assertNotIn("range", payload["ruleOfApplication"])
        # Optional fields should NOT be present
        self.assertNotIn("configurationData", payload)
        self.assertNotIn("order", payload)
        self.assertNotIn("pointcutData", payload)

    def test_create_automated_policy_custom_rule_of_application(self):
        """Test create_automated_policy with custom rule_of_application"""
        org_id = "o1"
        env_id = "e1"
        custom_extra = {"someCustomField": "value"}

        resp = make_response(
            status=201,
            json_body={"id": 101},
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/automated-policies",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        Policies(http).create_automated_policy(
            org_id=org_id,
            env_id=env_id,
            group_id="68ef9520-24e9-4cf2-b2f5-620025690913",
            asset_id="some-policy",
            asset_version="1.0.0",
            rule_of_application=custom_extra,
        )

        call = fake.calls[0]
        payload = call["json"]
        # Custom fields should be merged in
        self.assertEqual(payload["ruleOfApplication"]["someCustomField"], "value")
        # environmentId should still be set
        self.assertEqual(payload["ruleOfApplication"]["environmentId"], env_id)

    def test_create_automated_policy_with_pointcut_data(self):
        """Test create_automated_policy with pointcut data for resource-level policies"""
        org_id = "o1"
        env_id = "e1"
        pointcut = {"methodRegex": "GET", "uriTemplateRegex": "/users/.*"}

        resp = make_response(
            status=201,
            json_body={"id": 100},
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/automated-policies",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        Policies(http).create_automated_policy(
            org_id=org_id,
            env_id=env_id,
            group_id="68ef9520-24e9-4cf2-b2f5-620025690913",
            asset_id="rate-limiting",
            asset_version="1.5.1",
            pointcut_data=pointcut,
        )

        call = fake.calls[0]
        self.assertEqual(call["json"]["pointcutData"], pointcut)

    def test_create_automated_policy_handles_error(self):
        """Test create_automated_policy raises HttpError on failure"""
        org_id = "o1"
        env_id = "e1"

        resp = make_response(
            status=400,
            text="Bad Request: Invalid configuration",
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/automated-policies",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        with self.assertRaises(HttpError) as ctx:
            Policies(http).create_automated_policy(
                org_id=org_id,
                env_id=env_id,
                group_id="invalid-group",
                asset_id="nonexistent",
                asset_version="0.0.0",
            )

        self.assertEqual(ctx.exception.status, 400)

    def test_get_automated_policy_success(self):
        """Test get_automated_policy fetches a policy by ID"""
        org_id = "o1"
        policy_id = 12345

        current_policy = {
            "id": policy_id,
            "groupId": "68ef9520-24e9-4cf2-b2f5-620025690913",
            "assetId": "rate-limiting",
            "assetVersion": "1.5.1",
            "configurationData": {
                "rateLimits": [
                    {"timePeriodInMilliseconds": 60000, "maximumRequests": 100}
                ]
            },
            "order": 1,
            "disabled": False,
            "ruleOfApplication": {"environmentId": "e1", "organizationId": org_id},
        }

        resp = make_response(
            status=200,
            json_body=current_policy,
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/automated-policies/{policy_id}",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        result = Policies(http).get_automated_policy(org_id=org_id, policy_id=policy_id)

        call = fake.calls[0]
        self.assertEqual(call["method"], "GET")
        self.assertEqual(
            call["url"],
            f"{BASE}/apimanager/api/v1/organizations/{org_id}/automated-policies/{policy_id}",
        )
        self.assertEqual(result["id"], policy_id)
        self.assertEqual(result["assetId"], "rate-limiting")

    def test_get_automated_policy_not_found(self):
        """Test get_automated_policy raises HttpError for non-existent policy"""
        org_id = "o1"
        policy_id = 99999

        resp = make_response(
            status=404,
            text="Not Found",
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/automated-policies/{policy_id}",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        with self.assertRaises(HttpError) as ctx:
            Policies(http).get_automated_policy(org_id=org_id, policy_id=policy_id)

        self.assertEqual(ctx.exception.status, 404)

    def test_update_automated_policy_success(self):
        """Test update_automated_policy fetches current policy then sends PATCH"""
        org_id = "o1"
        policy_id = 12345
        new_config = {
            "rateLimits": [{"timePeriodInMilliseconds": 60000, "maximumRequests": 200}]
        }

        # First response: GET to fetch current policy
        current_policy = {
            "id": policy_id,
            "groupId": "68ef9520-24e9-4cf2-b2f5-620025690913",
            "assetId": "rate-limiting",
            "assetVersion": "1.5.1",
            "configurationData": {
                "rateLimits": [
                    {"timePeriodInMilliseconds": 60000, "maximumRequests": 100}
                ]
            },
            "order": 1,
            "disabled": False,
            "ruleOfApplication": {"environmentId": "e1", "organizationId": org_id},
        }
        get_resp = make_response(
            status=200,
            json_body=current_policy,
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/automated-policies/{policy_id}",
        )

        # Second response: PATCH response
        updated_policy = {
            "id": policy_id,
            "configurationData": new_config,
            "order": 2,
            "disabled": False,
        }
        patch_resp = make_response(
            status=200,
            json_body=updated_policy,
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/automated-policies/{policy_id}",
        )

        fake = FakeSession([get_resp, patch_resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        result = Policies(http).update_automated_policy(
            org_id=org_id,
            policy_id=policy_id,
            configuration_data=new_config,
            order=2,
        )

        # First call should be GET
        self.assertEqual(fake.calls[0]["method"], "GET")
        self.assertEqual(
            fake.calls[0]["url"],
            f"{BASE}/apimanager/api/v1/organizations/{org_id}/automated-policies/{policy_id}",
        )

        # Second call should be PATCH with full payload
        patch_call = fake.calls[1]
        self.assertEqual(patch_call["method"], "PATCH")
        self.assertEqual(
            patch_call["url"],
            f"{BASE}/apimanager/api/v1/organizations/{org_id}/automated-policies/{policy_id}",
        )
        self.assertEqual(patch_call["headers"]["Content-Type"], "application/json")
        # Should include required fields from current policy
        self.assertEqual(
            patch_call["json"]["groupId"], "68ef9520-24e9-4cf2-b2f5-620025690913"
        )
        self.assertEqual(patch_call["json"]["assetId"], "rate-limiting")
        self.assertEqual(patch_call["json"]["assetVersion"], "1.5.1")
        self.assertIn("ruleOfApplication", patch_call["json"])
        # Should include updated fields
        self.assertEqual(patch_call["json"]["configurationData"], new_config)
        self.assertEqual(patch_call["json"]["order"], 2)

        self.assertEqual(result["id"], policy_id)

    def test_update_automated_policy_disable(self):
        """Test update_automated_policy can disable a policy"""
        org_id = "o1"
        policy_id = 12345

        # First response: GET to fetch current policy
        current_policy = {
            "id": policy_id,
            "groupId": "68ef9520-24e9-4cf2-b2f5-620025690913",
            "assetId": "rate-limiting",
            "assetVersion": "1.5.1",
            "disabled": False,
            "ruleOfApplication": {"environmentId": "e1", "organizationId": org_id},
        }
        get_resp = make_response(
            status=200,
            json_body=current_policy,
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/automated-policies/{policy_id}",
        )

        # Second response: PATCH response
        patch_resp = make_response(
            status=200,
            json_body={"id": policy_id, "disabled": True},
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/automated-policies/{policy_id}",
        )
        fake = FakeSession([get_resp, patch_resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        result = Policies(http).update_automated_policy(
            org_id=org_id,
            policy_id=policy_id,
            disabled=True,
        )

        # PATCH call should have disabled=True
        patch_call = fake.calls[1]
        self.assertEqual(patch_call["json"]["disabled"], True)
        self.assertTrue(result["disabled"])

    def test_update_automated_policy_preserves_current_values(self):
        """Test update_automated_policy preserves current values when not updating"""
        org_id = "o1"
        policy_id = 12345

        # Current policy with existing values
        current_policy = {
            "id": policy_id,
            "groupId": "68ef9520-24e9-4cf2-b2f5-620025690913",
            "assetId": "rate-limiting",
            "assetVersion": "1.5.1",
            "configurationData": {"existingConfig": "value"},
            "order": 5,
            "disabled": True,
            "pointcutData": {"methodRegex": "GET"},
            "ruleOfApplication": {"environmentId": "e1", "organizationId": org_id},
        }
        get_resp = make_response(
            status=200,
            json_body=current_policy,
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/automated-policies/{policy_id}",
        )

        patch_resp = make_response(
            status=200,
            json_body={"id": policy_id},
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/automated-policies/{policy_id}",
        )
        fake = FakeSession([get_resp, patch_resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        # Call with no updates - should preserve all current values
        Policies(http).update_automated_policy(
            org_id=org_id,
            policy_id=policy_id,
        )

        patch_call = fake.calls[1]
        payload = patch_call["json"]
        # Required fields should be present
        self.assertEqual(payload["groupId"], "68ef9520-24e9-4cf2-b2f5-620025690913")
        self.assertEqual(payload["assetId"], "rate-limiting")
        self.assertEqual(payload["assetVersion"], "1.5.1")
        self.assertIn("ruleOfApplication", payload)
        # Current optional values should be preserved
        self.assertEqual(payload["configurationData"], {"existingConfig": "value"})
        self.assertEqual(payload["order"], 5)
        self.assertEqual(payload["disabled"], True)
        self.assertEqual(payload["pointcutData"], {"methodRegex": "GET"})

    def test_update_automated_policy_handles_not_found(self):
        """Test update_automated_policy raises HttpError for non-existent policy"""
        org_id = "o1"
        policy_id = 99999

        resp = make_response(
            status=404,
            text="Not Found",
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/automated-policies/{policy_id}",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        with self.assertRaises(HttpError) as ctx:
            Policies(http).update_automated_policy(
                org_id=org_id,
                policy_id=policy_id,
                disabled=True,
            )

        self.assertEqual(ctx.exception.status, 404)

    def test_delete_automated_policy_success(self):
        """Test delete_automated_policy sends DELETE request correctly"""
        org_id = "o1"
        policy_id = 12345

        resp = make_response(
            status=204,
            text="",
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/automated-policies/{policy_id}",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        # Should not raise
        Policies(http).delete_automated_policy(org_id=org_id, policy_id=policy_id)

        call = fake.calls[0]
        self.assertEqual(call["method"], "DELETE")
        self.assertEqual(
            call["url"],
            f"{BASE}/apimanager/api/v1/organizations/{org_id}/automated-policies/{policy_id}",
        )

    def test_delete_automated_policy_handles_not_found(self):
        """Test delete_automated_policy raises HttpError for non-existent policy"""
        org_id = "o1"
        policy_id = 99999

        resp = make_response(
            status=404,
            text="Not Found",
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/automated-policies/{policy_id}",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        with self.assertRaises(HttpError) as ctx:
            Policies(http).delete_automated_policy(org_id=org_id, policy_id=policy_id)

        self.assertEqual(ctx.exception.status, 404)

    def test_delete_automated_policy_string_policy_id(self):
        """Test delete_automated_policy works with string policy_id"""
        org_id = "o1"
        policy_id = "12345"  # String instead of int

        resp = make_response(
            status=204,
            text="",
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/automated-policies/{policy_id}",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        Policies(http).delete_automated_policy(org_id=org_id, policy_id=policy_id)

        call = fake.calls[0]
        self.assertIn(policy_id, call["url"])


if __name__ == "__main__":
    unittest.main()
