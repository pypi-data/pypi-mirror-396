import unittest

from anypoint_sdk._http import HttpClient, HttpError
from anypoint_sdk.resources.apis import APIs
from tests.fakes import FakeSession
from tests.helpers import make_response

BASE = "https://api.test.local"


class APIsCreateDeleteTests(unittest.TestCase):
    def test_create_instance_minimal_success(self):
        org_id = "o1"
        env_id = "e1"
        asset_id = "test-api"
        asset_version = "1.0.0"

        created_api = {
            "id": 12345,
            "assetId": asset_id,
            "assetVersion": asset_version,
            "technology": "mule4",
        }

        resp = make_response(
            status=200,
            json_body=created_api,
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/apis",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        result = APIs(http).create_instance(org_id, env_id, asset_id, asset_version)

        self.assertEqual(len(fake.calls), 1)
        call = fake.calls[0]
        self.assertEqual(call["method"], "POST")

        expected_payload = {
            "spec": {
                "assetId": asset_id,
                "version": asset_version,
            },
            "endpoint": {
                "type": "raml",
            },
            "technology": "mule4",
        }
        self.assertEqual(call["json"], expected_payload)
        self.assertEqual(result, created_api)

    def test_create_instance_with_all_options(self):
        org_id = "o1"
        env_id = "e1"
        asset_id = "full-api"
        asset_version = "2.0.0"
        product_version = "v2"
        instance_label = "production-api"
        upstream_url = "https://backend.example.com"
        proxy_uri = "https://proxy.example.com/api"

        created_api = {"id": 67890, "assetId": asset_id}

        resp = make_response(
            status=200,
            json_body=created_api,
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/apis",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        APIs(http).create_instance(
            org_id,
            env_id,
            asset_id,
            asset_version,
            product_version=product_version,
            instance_label=instance_label,
            upstream_url=upstream_url,
            proxy_uri=proxy_uri,
            technology="flexGateway",
        )

        call = fake.calls[0]
        expected_payload = {
            "spec": {
                "assetId": asset_id,
                "version": asset_version,
            },
            "endpoint": {
                "type": "raml",
                "uri": upstream_url,
                "proxyUri": proxy_uri,
            },
            "technology": "flexGateway",
            "productVersion": product_version,
            "instanceLabel": instance_label,
        }
        self.assertEqual(call["json"], expected_payload)

    def test_create_instance_handles_400_bad_request(self):
        org_id = "o1"
        env_id = "e1"

        resp = make_response(
            status=400,
            text="Bad Request",
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/apis",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        with self.assertRaises(HttpError) as ctx:
            APIs(http).create_instance(org_id, env_id, "test-api", "1.0.0")

        self.assertEqual(ctx.exception.status, 400)

    def test_delete_instance_success(self):
        org_id = "o1"
        env_id = "e1"
        api_id = 12345

        resp = make_response(
            status=204,
            text="",
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/apis/{api_id}",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        result = APIs(http).delete_instance(org_id, env_id, api_id)

        self.assertIsNone(result)
        self.assertEqual(len(fake.calls), 1)
        call = fake.calls[0]
        self.assertEqual(call["method"], "DELETE")
        self.assertEqual(
            call["url"],
            f"{BASE}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/apis/{api_id}",
        )

    def test_delete_instance_handles_404_not_found(self):
        org_id = "o1"
        env_id = "e1"
        api_id = 99999

        resp = make_response(
            status=404,
            text="Not Found",
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/apis/{api_id}",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        with self.assertRaises(HttpError) as ctx:
            APIs(http).delete_instance(org_id, env_id, api_id)

        self.assertEqual(ctx.exception.status, 404)

    def test_create_instance_handles_empty_response(self):
        org_id = "o1"
        env_id = "e1"

        resp = make_response(
            status=200,
            text="",
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/apis",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        result = APIs(http).create_instance(org_id, env_id, "test-api", "1.0.0")
        self.assertEqual(result, {})

    def test_update_instance_with_label(self):
        org_id = "o1"
        env_id = "e1"
        api_id = 12345

        updated_api = {
            "id": api_id,
            "instanceLabel": "new-label",
        }

        resp = make_response(
            status=200,
            json_body=updated_api,
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/apis/{api_id}",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        result = APIs(http).update_instance(
            org_id, env_id, api_id, instance_label="new-label"
        )

        self.assertEqual(len(fake.calls), 1)
        call = fake.calls[0]
        self.assertEqual(call["method"], "PATCH")
        self.assertEqual(call["json"], {"instanceLabel": "new-label"})
        self.assertEqual(result, updated_api)

    def test_update_instance_with_endpoint_options(self):
        org_id = "o1"
        env_id = "e1"
        api_id = 12345

        updated_api = {
            "id": api_id,
            "endpoint": {
                "uri": "https://new-backend.example.com",
                "proxyUri": "https://new-proxy.example.com",
                "isCloudHub": True,
            },
        }

        resp = make_response(
            status=200,
            json_body=updated_api,
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/apis/{api_id}",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        result = APIs(http).update_instance(
            org_id,
            env_id,
            api_id,
            upstream_url="https://new-backend.example.com",
            proxy_uri="https://new-proxy.example.com",
            is_cloud_hub=True,
        )

        call = fake.calls[0]
        self.assertEqual(call["method"], "PATCH")
        expected_payload = {
            "endpoint": {
                "uri": "https://new-backend.example.com",
                "proxyUri": "https://new-proxy.example.com",
                "isCloudHub": True,
            }
        }
        self.assertEqual(call["json"], expected_payload)

    def test_update_instance_with_all_options(self):
        org_id = "o1"
        env_id = "e1"
        api_id = 12345

        resp = make_response(
            status=200,
            json_body={"id": api_id},
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/apis/{api_id}",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        APIs(http).update_instance(
            org_id,
            env_id,
            api_id,
            instance_label="updated-api",
            upstream_url="https://backend.example.com",
            proxy_uri="https://proxy.example.com",
            is_cloud_hub=False,
            deployment_type="HY",
            response_timeout=30000,
            proxy_registration_uri="https://register.example.com",
        )

        call = fake.calls[0]
        expected_payload = {
            "instanceLabel": "updated-api",
            "endpoint": {
                "uri": "https://backend.example.com",
                "proxyUri": "https://proxy.example.com",
                "isCloudHub": False,
                "deploymentType": "HY",
                "responseTimeout": 30000,
                "proxyRegistrationUri": "https://register.example.com",
            },
        }
        self.assertEqual(call["json"], expected_payload)

    def test_update_instance_no_changes_returns_current(self):
        org_id = "o1"
        env_id = "e1"
        api_id = 12345

        current_api = {"id": api_id, "instanceLabel": "existing-label"}

        resp = make_response(
            status=200,
            json_body=current_api,
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/apis/{api_id}",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        # No update parameters provided - should call get_instance
        result = APIs(http).update_instance(org_id, env_id, api_id)

        self.assertEqual(len(fake.calls), 1)
        call = fake.calls[0]
        self.assertEqual(call["method"], "GET")  # Falls back to GET
        self.assertEqual(result, current_api)

    def test_update_instance_handles_404(self):
        org_id = "o1"
        env_id = "e1"
        api_id = 99999

        resp = make_response(
            status=404,
            text="Not Found",
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/apis/{api_id}",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        with self.assertRaises(HttpError) as ctx:
            APIs(http).update_instance(org_id, env_id, api_id, instance_label="new")

        self.assertEqual(ctx.exception.status, 404)

    def test_create_instance_with_group_id(self):
        org_id = "o1"
        env_id = "e1"
        asset_id = "test-api"
        asset_version = "1.0.0"
        group_id = "custom-group-id"

        created_api = {"id": 12345, "assetId": asset_id}

        resp = make_response(
            status=200,
            json_body=created_api,
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/apis",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        APIs(http).create_instance(
            org_id, env_id, asset_id, asset_version, group_id=group_id
        )

        call = fake.calls[0]
        self.assertEqual(call["json"]["spec"]["groupId"], group_id)

    def test_create_instance_with_promote(self):
        org_id = "o1"
        env_id = "e1"
        asset_id = "test-api"
        asset_version = "1.0.0"

        created_api = {"id": 12345, "assetId": asset_id}

        resp = make_response(
            status=200,
            json_body=created_api,
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/apis",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        APIs(http).create_instance(
            org_id, env_id, asset_id, asset_version, promote=True
        )

        call = fake.calls[0]
        self.assertTrue(call["json"]["promote"])

    def test_create_instance_with_is_cloud_hub(self):
        org_id = "o1"
        env_id = "e1"
        asset_id = "test-api"
        asset_version = "1.0.0"

        created_api = {"id": 12345, "assetId": asset_id}

        resp = make_response(
            status=200,
            json_body=created_api,
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/apis",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        APIs(http).create_instance(
            org_id, env_id, asset_id, asset_version, is_cloud_hub=True
        )

        call = fake.calls[0]
        self.assertTrue(call["json"]["endpoint"]["isCloudHub"])


if __name__ == "__main__":
    unittest.main()
