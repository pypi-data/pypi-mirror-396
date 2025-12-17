import unittest

from anypoint_sdk._http import HttpClient, HttpError
from anypoint_sdk.resources.exchange import Exchange
from tests.fakes import FakeSession
from tests.helpers import make_response

BASE = "https://api.test.local"


class ExchangeTests(unittest.TestCase):

    def test_create_asset_handles_400_bad_request(self):
        org_id = "o1"

        resp = make_response(
            status=400,
            text="Bad Request: Asset already exists",
            url=f"{BASE}/exchange/api/v2/organizations/{org_id}/assets",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        with self.assertRaises(HttpError) as ctx:
            Exchange(http).create_asset(org_id, "test-api", "Test", "1.0.0")

        self.assertEqual(ctx.exception.status, 400)

    def test_delete_asset_success_with_soft_delete(self):
        org_id = "o1"
        group_id = "g1"
        asset_id = "test-api"
        version = "1.0.0"

        resp = make_response(
            status=204,
            text="",
            url=f"{BASE}/exchange/api/v1/organizations/{org_id}/assets/{group_id}/{asset_id}/{version}",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        result = Exchange(http).delete_asset(
            org_id, group_id, asset_id, version, delete_type="soft-delete"
        )

        self.assertIsNone(result)
        call = fake.calls[0]
        self.assertEqual(call["headers"]["X-Delete-Type"], "soft-delete")

    def test_delete_asset_success_with_default_hard_delete(self):
        org_id = "o1"
        group_id = "g1"
        asset_id = "test-api"
        version = "1.0.0"

        resp = make_response(
            status=204,
            text="",
            url=f"{BASE}/exchange/api/v1/organizations/{org_id}/assets/{group_id}/{asset_id}/{version}",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        result = Exchange(http).delete_asset(org_id, group_id, asset_id, version)

        self.assertIsNone(result)
        self.assertEqual(len(fake.calls), 1)
        call = fake.calls[0]
        self.assertEqual(call["method"], "DELETE")
        self.assertEqual(
            call["url"],
            f"{BASE}/exchange/api/v1/organizations/{org_id}/assets/{group_id}/{asset_id}/{version}",
        )
        self.assertEqual(call["headers"]["X-Delete-Type"], "hard-delete")

    def test_delete_asset_handles_404_not_found(self):
        org_id = "o1"
        group_id = "g1"
        asset_id = "missing-api"
        version = "1.0.0"

        resp = make_response(
            status=404,
            text="Not Found",
            url=f"{BASE}/exchange/api/v1/organizations/{org_id}/assets/{group_id}/{asset_id}/{version}",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        with self.assertRaises(HttpError) as ctx:
            Exchange(http).delete_asset(org_id, group_id, asset_id, version)

        self.assertEqual(ctx.exception.status, 404)

    def test_delete_asset_handles_403_forbidden(self):
        org_id = "o1"
        group_id = "g1"
        asset_id = "test-api"
        version = "1.0.0"

        resp = make_response(
            status=403,
            text="Forbidden - insufficient permissions",
            url=f"{BASE}/exchange/api/v1/organizations/{org_id}/assets/{group_id}/{asset_id}/{version}",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        with self.assertRaises(HttpError) as ctx:
            Exchange(http).delete_asset(org_id, group_id, asset_id, version)

        self.assertEqual(ctx.exception.status, 403)

    def test_list_assets_success(self):
        assets_payload = [
            {
                "groupId": "o1",
                "assetId": "api-1",
                "version": "1.0.0",
                "name": "Test API 1",
                "description": "A test API",
                "type": "rest-api",
                "classifier": "raml",
                "status": "published",
            },
            {
                "groupId": "o1",
                "assetId": "api-2",
                "version": "2.0.0",
                "name": "Test API 2",
                "type": "rest-api",
                "classifier": "oas",
                "status": "published",
            },
        ]

        resp = make_response(
            status=200,
            json_body=assets_payload,
            url=f"{BASE}/exchange/api/v2/assets",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        result = Exchange(http).list_assets()

        self.assertEqual(len(fake.calls), 1)
        call = fake.calls[0]
        self.assertEqual(call["method"], "GET")
        self.assertEqual(call["url"], f"{BASE}/exchange/api/v2/assets")

        self.assertEqual(len(result), 2)
        asset_ids = {a["assetId"] for a in result}
        self.assertEqual(asset_ids, {"api-1", "api-2"})

    def test_list_assets_with_parameters(self):
        resp = make_response(
            status=200,
            json_body=[],
            url=f"{BASE}/exchange/api/v2/assets",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        Exchange(http).list_assets(
            search="test", type_filter="rest-api", offset=10, limit=50
        )

        call = fake.calls[0]
        expected_params = {
            "search": "test",
            "type": "rest-api",
            "offset": 10,
            "limit": 50,
        }
        self.assertEqual(call["params"], expected_params)

    def test_create_asset_minimal_success(self):
        org_id = "o1"
        asset_id = "new-api"
        name = "New Test API"
        version = "1.0.0"

        created_asset = {
            "groupId": org_id,
            "assetId": asset_id,
            "version": version,
            "name": name,
            "type": "rest-api",
            "status": "published",
        }

        resp = make_response(
            status=200,
            json_body=created_asset,
            url=f"{BASE}/exchange/api/v2/organizations/{org_id}/assets/{org_id}/{asset_id}/{version}",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        result = Exchange(http).create_asset(org_id, asset_id, name, version)

        self.assertEqual(len(fake.calls), 1)
        call = fake.calls[0]
        self.assertEqual(call["method"], "POST")
        self.assertEqual(
            call["url"],
            f"{BASE}/exchange/api/v2/organizations/{org_id}/assets/{org_id}/{asset_id}/{version}",
        )

        expected_files = {
            "name": (None, name),
            "type": (None, "rest-api"),
        }
        self.assertEqual(call["files"], expected_files)
        self.assertEqual(result, created_asset)

    def test_create_asset_with_all_options(self):
        org_id = "o1"
        asset_id = "full-api"
        name = "Full Test API"
        version = "2.0.0"
        description = "A complete test API"
        group_id = "custom-group"

        resp = make_response(
            status=200,
            json_body={"assetId": asset_id},
            url=f"{BASE}/exchange/api/v2/organizations/{org_id}/assets/{group_id}/{asset_id}/{version}",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        Exchange(http).create_asset(
            org_id,
            asset_id,
            name,
            version,
            description=description,
            asset_type="soap-api",
            group_id=group_id,
        )

        call = fake.calls[0]
        expected_files = {
            "name": (None, name),
            "description": (None, description),
            "type": (None, "soap-api"),
        }
        self.assertEqual(call["files"], expected_files)

    def test_list_assets_handles_non_list_response(self):
        resp = make_response(
            status=200,
            json_body={"error": "unexpected format"},
            url=f"{BASE}/exchange/api/v2/assets",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        result = Exchange(http).list_assets()
        self.assertEqual(result, [])

    def test_list_assets_ignores_non_dict_entries(self):
        """Test that non-dict entries in the assets array are ignored"""
        assets_payload = [
            {
                "groupId": "o1",
                "assetId": "api-1",
                "version": "1.0.0",
                "name": "Valid API",
            },
            "not-a-dict",  # Should be ignored
            123,  # Should be ignored
            None,  # Should be ignored
            {
                "groupId": "o1",
                "assetId": "api-2",
                "version": "2.0.0",
                "name": "Another Valid API",
            },
        ]

        resp = make_response(
            status=200,
            json_body=assets_payload,
            url=f"{BASE}/exchange/api/v2/assets",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        result = Exchange(http).list_assets()

        # Should only include the 2 valid dict entries, ignoring non-dict items
        self.assertEqual(len(result), 2)
        asset_ids = {a["assetId"] for a in result}
        self.assertEqual(asset_ids, {"api-1", "api-2"})

    def test_create_asset_handles_empty_response(self):
        org_id = "o1"

        resp = make_response(
            status=200,
            text="",
            url=f"{BASE}/exchange/api/v2/organizations/{org_id}/assets/{org_id}/test-api/1.0.0",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        result = Exchange(http).create_asset(org_id, "test-api", "Test", "1.0.0")
        self.assertEqual(result, {})

    def test_dedupe_skips_assets_with_empty_key_fields(self):
        """Test that assets with empty groupId, assetId, or version are skipped during dedup"""
        assets_payload = [
            {
                "groupId": "o1",
                "assetId": "api-1",
                "version": "1.0.0",
                "name": "Valid API 1",
            },
            {
                "groupId": "o1",
                "assetId": "api-1",
                "version": "1.0.0",
                "name": "Duplicate API 1",  # Should be deduped
            },
            {
                "groupId": "o1",
                "assetId": "api-2",
                "version": "2.0.0",
                "name": "Valid API 2",
            },
        ]

        resp = make_response(
            status=200,
            json_body=assets_payload,
            url=f"{BASE}/exchange/api/v2/assets",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        result = Exchange(http).list_assets()

        # Should dedupe by (groupId, assetId, version) key, keeping first occurrence
        self.assertEqual(len(result), 2)
        asset_ids = {a["assetId"] for a in result}
        self.assertEqual(asset_ids, {"api-1", "api-2"})

        # First occurrence should be kept
        api1 = next(a for a in result if a["assetId"] == "api-1")
        self.assertEqual(api1["name"], "Valid API 1")

    def test_list_assets_with_organization_filter(self):
        org_id = "test-org-123"
        assets_payload = [{"groupId": org_id, "assetId": "org-api", "version": "1.0.0"}]

        resp = make_response(
            status=200,
            json_body=assets_payload,
            url=f"{BASE}/exchange/api/v2/assets",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        Exchange(http).list_assets(org_id=org_id)

        call = fake.calls[0]
        expected_params = {
            "offset": 0,
            "limit": 100,
            "organizationIds": [org_id],  # Verify this is sent
        }
        self.assertEqual(call["params"], expected_params)

    def test_check_publication_status_with_full_url(self):
        """Test check_publication_status with full URL"""
        status_response = {"status": "completed", "assetId": "test-api"}

        resp = make_response(
            status=200,
            json_body=status_response,
            url=f"{BASE}/exchange/api/v2/organizations/org1/assets/group1/test-api/1.0.0/publication/status/123",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        full_url = "https://anypoint.mulesoft.com/exchange/api/v2/organizations/org1/assets/group1/test-api/1.0.0/publication/status/123"
        result = Exchange(http).check_publication_status(full_url)

        # Should strip the base URL and use just the path
        call = fake.calls[0]
        self.assertEqual(
            call["url"],
            f"{BASE}/exchange/api/v2/organizations/org1/assets/group1/test-api/1.0.0/publication/status/123",
        )
        self.assertEqual(result, status_response)

    def test_check_publication_status_with_path_only(self):
        """Test check_publication_status with path only"""
        status_response = {"status": "running"}

        resp = make_response(
            status=200,
            json_body=status_response,
            url=f"{BASE}/api/v2/status/456",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        path_only = "/api/v2/status/456"
        result = Exchange(http).check_publication_status(path_only)

        # Should use the path as-is
        call = fake.calls[0]
        self.assertEqual(call["url"], f"{BASE}/api/v2/status/456")
        self.assertEqual(result, status_response)

    def test_check_publication_status_empty_response(self):
        """Test check_publication_status with empty response"""
        resp = make_response(
            status=200,
            text="",  # Empty response
            url=f"{BASE}/api/v2/status/789",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        result = Exchange(http).check_publication_status("/api/v2/status/789")
        self.assertEqual(result, {})  # Should return empty dict for empty response

    def test_list_assets_for_org_filters_by_group_id(self):
        """Test list_assets_for_org filters assets by groupId matching org_id"""
        org_id = "target-org"
        other_org = "other-org"

        all_assets = [
            {"groupId": org_id, "assetId": "api-1", "name": "API 1"},
            {"groupId": other_org, "assetId": "api-2", "name": "API 2"},
            {"groupId": org_id, "assetId": "api-3", "name": "API 3"},
            {"groupId": "third-org", "assetId": "api-4", "name": "API 4"},
        ]

        resp = make_response(
            status=200,
            json_body=all_assets,
            url=f"{BASE}/exchange/api/v2/assets",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        result = Exchange(http).list_assets_for_org(org_id)

        # Should only return assets where groupId matches org_id
        self.assertEqual(len(result), 2)
        asset_ids = {a["assetId"] for a in result}
        self.assertEqual(asset_ids, {"api-1", "api-3"})

    def test_list_assets_for_org_with_limit(self):
        """Test list_assets_for_org respects limit parameter"""
        org_id = "target-org"

        # Create 5 assets for the org
        all_assets = [
            {"groupId": org_id, "assetId": f"api-{i}", "name": f"API {i}"}
            for i in range(5)
        ]

        resp = make_response(
            status=200,
            json_body=all_assets,
            url=f"{BASE}/exchange/api/v2/assets",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        result = Exchange(http).list_assets_for_org(org_id, limit=3)

        # Should only return 3 assets despite 5 being available
        self.assertEqual(len(result), 3)

    def test_list_assets_for_org_with_search_filter(self):
        """Test list_assets_for_org applies search filter"""
        org_id = "target-org"

        all_assets = [
            {"groupId": org_id, "assetId": "user-api", "name": "User Management API"},
            {"groupId": org_id, "assetId": "order-api", "name": "Order Processing API"},
            {"groupId": org_id, "assetId": "payment-api", "name": "Payment Gateway"},
        ]

        resp = make_response(
            status=200,
            json_body=all_assets,
            url=f"{BASE}/exchange/api/v2/assets",
        )

        # First test - search by name
        fake1 = FakeSession([resp])
        http1 = HttpClient(base_url=BASE, session=fake1, retries=0)
        result = Exchange(http1).list_assets_for_org(org_id, search="management")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["assetId"], "user-api")

        # Second test - search by assetId
        fake2 = FakeSession([resp])
        http2 = HttpClient(base_url=BASE, session=fake2, retries=0)
        result = Exchange(http2).list_assets_for_org(org_id, search="order")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["assetId"], "order-api")

    def test_list_assets_for_org_case_insensitive_search(self):
        """Test list_assets_for_org search is case insensitive"""
        org_id = "target-org"

        all_assets = [
            {"groupId": org_id, "assetId": "user-api", "name": "User Management API"},
        ]

        resp = make_response(
            status=200,
            json_body=all_assets,
            url=f"{BASE}/exchange/api/v2/assets",
        )

        # First test - uppercase search
        fake1 = FakeSession([resp])
        http1 = HttpClient(base_url=BASE, session=fake1, retries=0)
        result = Exchange(http1).list_assets_for_org(org_id, search="USER")
        self.assertEqual(len(result), 1)

        # Second test - lowercase search
        fake2 = FakeSession([resp])
        http2 = HttpClient(base_url=BASE, session=fake2, retries=0)
        result = Exchange(http2).list_assets_for_org(org_id, search="management")
        self.assertEqual(len(result), 1)

    def test_list_resources_published_success(self):
        """Test list_resources for published resources"""
        group_id = "group1"
        asset_id = "test-api"
        version = "1.0.0"

        resources_response = [
            {"path": "api.raml", "name": "Main API spec", "size": 1024},
            {"path": "types/user.raml", "name": "User types", "size": 512},
        ]

        resp = make_response(
            status=200,
            json_body=resources_response,
            url=f"{BASE}/exchange/api/v2/assets/{group_id}/{asset_id}/{version}/portal/resources",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        result = Exchange(http).list_resources(group_id, asset_id, version, draft=False)

        call = fake.calls[0]
        self.assertEqual(call["method"], "GET")
        self.assertEqual(
            call["url"],
            f"{BASE}/exchange/api/v2/assets/{group_id}/{asset_id}/{version}/portal/resources",
        )
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["path"], "api.raml")
        self.assertEqual(result[1]["path"], "types/user.raml")

    def test_list_resources_draft_success(self):
        """Test list_resources for draft resources"""
        group_id = "group1"
        asset_id = "test-api"
        version = "1.0.0"

        resources_response = [
            {"path": "draft-api.raml", "name": "Draft API spec", "size": 2048},
        ]

        resp = make_response(
            status=200,
            json_body=resources_response,
            url=f"{BASE}/exchange/api/v2/assets/{group_id}/{asset_id}/{version}/portal/draft/resources",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        result = Exchange(http).list_resources(group_id, asset_id, version, draft=True)

        call = fake.calls[0]
        expected_url = f"{BASE}/exchange/api/v2/assets/{group_id}/{asset_id}/{version}/portal/draft/resources"
        self.assertEqual(call["url"], expected_url)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["path"], "draft-api.raml")

    def test_list_resources_empty_response(self):
        """Test list_resources with empty response"""
        resp = make_response(
            status=200,
            json_body=[],
            url=f"{BASE}/exchange/api/v2/assets/g1/a1/1.0.0/portal/resources",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        result = Exchange(http).list_resources("g1", "a1", "1.0.0")
        self.assertEqual(result, [])

    def test_list_resources_filters_invalid_entries(self):
        """Test list_resources filters out entries without path"""
        resources_response = [
            {"path": "valid.raml", "size": 1024},
            {"name": "no-path-entry", "size": 512},  # Should be filtered out
            "not-a-dict",  # Should be filtered out
            {"path": "another-valid.raml", "size": 256},
        ]

        resp = make_response(
            status=200,
            json_body=resources_response,
            url=f"{BASE}/exchange/api/v2/assets/g1/a1/1.0.0/portal/resources",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        result = Exchange(http).list_resources("g1", "a1", "1.0.0")

        # Should only include entries that are dicts with 'path'
        self.assertEqual(len(result), 2)
        paths = [r["path"] for r in result]
        self.assertEqual(paths, ["valid.raml", "another-valid.raml"])

    def test_delete_resource_success(self):
        """Test delete_resource successfully deletes a resource"""
        group_id = "group1"
        asset_id = "test-api"
        version = "1.0.0"
        resource_path = "api.raml"

        resp = make_response(
            status=204,
            text="",
            url=f"{BASE}/exchange/api/v2/assets/{group_id}/{asset_id}/{version}/portal/draft/{resource_path}",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        Exchange(http).delete_resource(group_id, asset_id, version, resource_path)

        call = fake.calls[0]
        self.assertEqual(call["method"], "DELETE")
        expected_url = f"{BASE}/exchange/api/v2/assets/{group_id}/{asset_id}/{version}/portal/draft/{resource_path}"
        self.assertEqual(call["url"], expected_url)

    def test_delete_resource_handles_404(self):
        """Test delete_resource handles 404 not found"""
        resp = make_response(
            status=404,
            text="Resource not found",
            url=f"{BASE}/exchange/api/v2/assets/g1/a1/1.0.0/portal/draft/missing.raml",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        with self.assertRaises(HttpError) as ctx:
            Exchange(http).delete_resource("g1", "a1", "1.0.0", "missing.raml")

        self.assertEqual(ctx.exception.status, 404)

    def test_delete_resource_with_nested_path(self):
        """Test delete_resource with nested resource path"""
        group_id = "group1"
        asset_id = "test-api"
        version = "1.0.0"
        resource_path = "types/user.raml"

        resp = make_response(
            status=204,
            text="",
            url=f"{BASE}/exchange/api/v2/assets/{group_id}/{asset_id}/{version}/portal/draft/{resource_path}",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        Exchange(http).delete_resource(group_id, asset_id, version, resource_path)

        call = fake.calls[0]
        expected_url = f"{BASE}/exchange/api/v2/assets/{group_id}/{asset_id}/{version}/portal/draft/types/user.raml"
        self.assertEqual(call["url"], expected_url)

    def test_download_resource_published_success(self):
        """Test download_resource for published resource"""
        import os
        import tempfile

        group_id = "group1"
        asset_id = "test-api"
        version = "1.0.0"
        resource_path = "api.raml"

        raml_content = "#%RAML 1.0\ntitle: Test API\n"

        resp = make_response(
            status=200,
            text=raml_content,
            url=f"{BASE}/exchange/api/v2/assets/{group_id}/{asset_id}/{version}/portal/{resource_path}",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tmp_file:
            tmp_path = tmp_file.name

        try:
            Exchange(http).download_resource(
                group_id, asset_id, version, resource_path, tmp_path, draft=False
            )

            # Verify the request
            call = fake.calls[0]
            expected_url = f"{BASE}/exchange/api/v2/assets/{group_id}/{asset_id}/{version}/portal/{resource_path}"
            self.assertEqual(call["url"], expected_url)

            # Verify file was written
            with open(tmp_path, "r") as f:
                content = f.read()
            self.assertEqual(content, raml_content)

        finally:
            os.unlink(tmp_path)

    def test_download_resource_draft_success(self):
        """Test download_resource for draft resource"""
        import os
        import tempfile

        group_id = "group1"
        asset_id = "test-api"
        version = "1.0.0"
        resource_path = "draft-api.raml"

        raml_content = "#%RAML 1.0\ntitle: Draft API\n"

        resp = make_response(
            status=200,
            text=raml_content,
            url=f"{BASE}/exchange/api/v2/assets/{group_id}/{asset_id}/{version}/portal/draft/{resource_path}",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tmp_file:
            tmp_path = tmp_file.name

        try:
            Exchange(http).download_resource(
                group_id, asset_id, version, resource_path, tmp_path, draft=True
            )

            call = fake.calls[0]
            expected_url = f"{BASE}/exchange/api/v2/assets/{group_id}/{asset_id}/{version}/portal/draft/{resource_path}"
            self.assertEqual(call["url"], expected_url)

            with open(tmp_path, "r") as f:
                content = f.read()
            self.assertEqual(content, raml_content)

        finally:
            os.unlink(tmp_path)

    def test_download_resource_handles_404(self):
        """Test download_resource handles missing resource"""
        resp = make_response(
            status=404,
            text="Resource not found",
            url=f"{BASE}/exchange/api/v2/assets/g1/a1/1.0.0/portal/missing.raml",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        with self.assertRaises(HttpError) as ctx:
            Exchange(http).download_resource(
                "g1", "a1", "1.0.0", "missing.raml", "/tmp/test"
            )

        self.assertEqual(ctx.exception.status, 404)

    def test_upload_resource_success(self):
        """Test upload_resource successfully uploads a file"""
        import os
        import tempfile

        group_id = "group1"
        asset_id = "test-api"
        version = "1.0.0"

        # Create a temporary RAML file
        raml_content = "#%RAML 1.0\ntitle: Test API\n"
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".raml", delete=False
        ) as tmp_file:
            tmp_file.write(raml_content)
            tmp_path = tmp_file.name

        upload_response = {"message": "Resource uploaded successfully"}

        resp = make_response(
            status=200,
            json_body=upload_response,
            url=f"{BASE}/exchange/api/v2/assets/{group_id}/{asset_id}/{version}/portal/draft/resources",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        try:
            result = Exchange(http).upload_resource(
                group_id, asset_id, version, tmp_path
            )

            # Verify the request
            call = fake.calls[0]
            self.assertEqual(call["method"], "POST")
            expected_url = f"{BASE}/exchange/api/v2/assets/{group_id}/{asset_id}/{version}/portal/draft/resources"
            self.assertEqual(call["url"], expected_url)

            # Verify the file was included in the form data
            self.assertIn("file", call["files"])
            filename, content, content_type = call["files"]["file"]
            self.assertEqual(filename, os.path.basename(tmp_path))
            self.assertEqual(content.decode(), raml_content)
            self.assertEqual(content_type, "application/octet-stream")

            self.assertEqual(result, upload_response)

        finally:
            os.unlink(tmp_path)

    def test_upload_resource_with_custom_name(self):
        """Test upload_resource with custom resource name"""
        import os
        import tempfile

        raml_content = "#%RAML 1.0\ntitle: Custom API\n"
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".raml", delete=False
        ) as tmp_file:
            tmp_file.write(raml_content)
            tmp_path = tmp_file.name

        resp = make_response(
            status=200,
            json_body={"success": True},
            url=f"{BASE}/exchange/api/v2/assets/g1/a1/1.0.0/portal/draft/resources",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        try:
            Exchange(http).upload_resource(
                "g1", "a1", "1.0.0", tmp_path, resource_name="custom-api.raml"
            )

            call = fake.calls[0]
            filename, content, content_type = call["files"]["file"]
            self.assertEqual(filename, "custom-api.raml")

        finally:
            os.unlink(tmp_path)

    def test_upload_resource_handles_file_not_found(self):
        """Test upload_resource handles missing file"""
        fake = FakeSession([])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        with self.assertRaises(FileNotFoundError):
            Exchange(http).upload_resource(
                "g1", "a1", "1.0.0", "/nonexistent/file.raml"
            )

    def test_list_resources_handles_non_list_response(self):
        """Test list_resources when API returns non-list (e.g., error object)"""
        resp = make_response(
            status=200,
            json_body={"error": "unexpected format"},
            url=f"{BASE}/exchange/api/v2/assets/g1/a1/1.0.0/portal/resources",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        result = Exchange(http).list_resources("g1", "a1", "1.0.0")
        self.assertEqual(result, [])

    def test_create_asset_with_raml_bundle_success(self):
        """Test create_asset_with_raml_bundle successfully creates asset"""
        import os
        import tempfile
        import zipfile

        org_id = "org1"
        group_id = "group1"
        asset_id = "test-api"
        version = "1.0.0"

        # Create a temporary ZIP file with RAML content
        tmpdir = tempfile.mkdtemp()
        zip_path = os.path.join(tmpdir, "test-raml.zip")
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("api.raml", "#%RAML 1.0\ntitle: Test API\n")

        created_asset = {
            "groupId": group_id,
            "assetId": asset_id,
            "version": version,
            "status": "published",
        }

        resp = make_response(
            status=201,
            json_body=created_asset,
            url=f"{BASE}/exchange/api/v2/organizations/{org_id}/assets/{group_id}/{asset_id}/{version}",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        try:
            result = Exchange(http).create_asset_with_raml_bundle(
                org_id=org_id,
                group_id=group_id,
                asset_id=asset_id,
                version=version,
                raml_zip_path=zip_path,
                name="Test RAML API",
                description="Test description",
            )

            call = fake.calls[0]
            self.assertEqual(call["method"], "POST")
            self.assertEqual(
                call["url"],
                f"{BASE}/exchange/api/v2/organizations/{org_id}/assets/{group_id}/{asset_id}/{version}",
            )
            # Verify sync publication header
            self.assertEqual(call["headers"]["x-sync-publication"], "true")
            self.assertEqual(result, created_asset)
        finally:
            os.unlink(zip_path)
            os.rmdir(tmpdir)

    def test_create_asset_with_raml_bundle_file_not_found(self):
        """Test create_asset_with_raml_bundle raises FileNotFoundError for missing ZIP"""
        fake = FakeSession([])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        with self.assertRaises(FileNotFoundError) as ctx:
            Exchange(http).create_asset_with_raml_bundle(
                org_id="org1",
                group_id="group1",
                asset_id="test-api",
                version="1.0.0",
                raml_zip_path="/nonexistent/path.zip",
                name="Test API",
            )
        self.assertIn("RAML ZIP file not found", str(ctx.exception))

    def test_create_asset_with_raml_bundle_handles_409_conflict(self):
        """Test create_asset_with_raml_bundle handles 409 conflict error"""
        import os
        import tempfile
        import zipfile

        org_id = "org1"
        group_id = "group1"
        asset_id = "existing-api"
        version = "1.0.0"

        # Create a temporary ZIP file
        tmpdir = tempfile.mkdtemp()
        zip_path = os.path.join(tmpdir, "test-raml.zip")
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("api.raml", "#%RAML 1.0\ntitle: Test\n")

        resp = make_response(
            status=409,
            text="Asset already exists",
            url=f"{BASE}/exchange/api/v2/organizations/{org_id}/assets/{group_id}/{asset_id}/{version}",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        try:
            with self.assertRaises(HttpError) as ctx:
                Exchange(http).create_asset_with_raml_bundle(
                    org_id=org_id,
                    group_id=group_id,
                    asset_id=asset_id,
                    version=version,
                    raml_zip_path=zip_path,
                    name="Test API",
                )
            self.assertEqual(ctx.exception.status, 409)
            # The error body contains the response text
            self.assertIn("already exists", ctx.exception.body)
        finally:
            os.unlink(zip_path)
            os.rmdir(tmpdir)

    def test_create_asset_with_raml_bundle_handles_other_http_errors(self):
        """Test create_asset_with_raml_bundle handles non-409 HTTP errors"""
        import os
        import tempfile
        import zipfile

        org_id = "org1"
        group_id = "group1"
        asset_id = "test-api"
        version = "1.0.0"

        # Create a temporary ZIP file
        tmpdir = tempfile.mkdtemp()
        zip_path = os.path.join(tmpdir, "test-raml.zip")
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("api.raml", "#%RAML 1.0\n")

        resp = make_response(
            status=400,
            text="Bad Request: Invalid RAML",
            url=f"{BASE}/exchange/api/v2/organizations/{org_id}/assets/{group_id}/{asset_id}/{version}",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        try:
            with self.assertRaises(HttpError) as ctx:
                Exchange(http).create_asset_with_raml_bundle(
                    org_id=org_id,
                    group_id=group_id,
                    asset_id=asset_id,
                    version=version,
                    raml_zip_path=zip_path,
                    name="Test API",
                )
            self.assertEqual(ctx.exception.status, 400)
        finally:
            os.unlink(zip_path)
            os.rmdir(tmpdir)

    def test_create_asset_with_raml_bundle_without_sync_publication(self):
        """Test create_asset_with_raml_bundle with sync_publication=False"""
        import os
        import tempfile
        import zipfile

        org_id = "org1"
        group_id = "group1"
        asset_id = "test-api"
        version = "1.0.0"

        tmpdir = tempfile.mkdtemp()
        zip_path = os.path.join(tmpdir, "test-raml.zip")
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("api.raml", "#%RAML 1.0\n")

        resp = make_response(
            status=202,
            json_body={"status": "pending"},
            url=f"{BASE}/exchange/api/v2/organizations/{org_id}/assets/{group_id}/{asset_id}/{version}",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        try:
            Exchange(http).create_asset_with_raml_bundle(
                org_id=org_id,
                group_id=group_id,
                asset_id=asset_id,
                version=version,
                raml_zip_path=zip_path,
                name="Test API",
                sync_publication=False,
            )

            call = fake.calls[0]
            # Should not have sync publication header
            self.assertNotIn("x-sync-publication", call["headers"])
        finally:
            os.unlink(zip_path)
            os.rmdir(tmpdir)

    def test_create_asset_with_raml_bundle_empty_response(self):
        """Test create_asset_with_raml_bundle handles empty response body"""
        import os
        import tempfile
        import zipfile

        org_id = "org1"
        group_id = "group1"
        asset_id = "test-api"
        version = "1.0.0"

        tmpdir = tempfile.mkdtemp()
        zip_path = os.path.join(tmpdir, "test-raml.zip")
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("api.raml", "#%RAML 1.0\n")

        resp = make_response(
            status=201,
            text="",  # Empty response
            url=f"{BASE}/exchange/api/v2/organizations/{org_id}/assets/{group_id}/{asset_id}/{version}",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        try:
            result = Exchange(http).create_asset_with_raml_bundle(
                org_id=org_id,
                group_id=group_id,
                asset_id=asset_id,
                version=version,
                raml_zip_path=zip_path,
                name="Test API",
            )
            self.assertEqual(result, {})
        finally:
            os.unlink(zip_path)
            os.rmdir(tmpdir)

    def test_create_raml_zip_bundle_basic(self):
        """Test create_raml_zip_bundle creates valid ZIP with RAML content"""
        import os
        import zipfile

        fake = FakeSession([])
        http = HttpClient(base_url=BASE, session=fake, retries=0)
        exchange = Exchange(http)

        raml_content = "#%RAML 1.0\ntitle: Test API\nversion: v1\n"

        zip_path = exchange.create_raml_zip_bundle(raml_content)

        try:
            # Verify ZIP was created
            self.assertTrue(os.path.exists(zip_path))

            # Verify ZIP contents
            with zipfile.ZipFile(zip_path, "r") as zf:
                names = zf.namelist()
                self.assertIn("api.raml", names)

                content = zf.read("api.raml").decode()
                self.assertEqual(content, raml_content)
        finally:
            os.unlink(zip_path)
            os.rmdir(os.path.dirname(zip_path))

    def test_create_raml_zip_bundle_custom_main_file(self):
        """Test create_raml_zip_bundle with custom main file name"""
        import os
        import zipfile

        fake = FakeSession([])
        http = HttpClient(base_url=BASE, session=fake, retries=0)
        exchange = Exchange(http)

        raml_content = "#%RAML 1.0\ntitle: Custom\n"

        zip_path = exchange.create_raml_zip_bundle(
            raml_content, main_file="custom-api.raml"
        )

        try:
            with zipfile.ZipFile(zip_path, "r") as zf:
                names = zf.namelist()
                self.assertIn("custom-api.raml", names)
                self.assertNotIn("api.raml", names)
        finally:
            os.unlink(zip_path)
            os.rmdir(os.path.dirname(zip_path))

    def test_create_raml_zip_bundle_with_additional_files(self):
        """Test create_raml_zip_bundle with additional files"""
        import os
        import zipfile

        fake = FakeSession([])
        http = HttpClient(base_url=BASE, session=fake, retries=0)
        exchange = Exchange(http)

        main_raml = "#%RAML 1.0\ntitle: Main API\n"
        additional_files = {
            "types/user.raml": "#%RAML 1.0 DataType\ntype: object\n",
            "traits/secured.raml": "#%RAML 1.0 Trait\n",
        }

        zip_path = exchange.create_raml_zip_bundle(
            main_raml, additional_files=additional_files
        )

        try:
            with zipfile.ZipFile(zip_path, "r") as zf:
                names = zf.namelist()
                self.assertIn("api.raml", names)
                self.assertIn("types/user.raml", names)
                self.assertIn("traits/secured.raml", names)

                # Verify content
                user_content = zf.read("types/user.raml").decode()
                self.assertIn("DataType", user_content)
        finally:
            os.unlink(zip_path)
            os.rmdir(os.path.dirname(zip_path))

    def test_create_policy_definition_success(self):
        """Test create_policy_definition successfully creates a policy asset"""
        org_id = "org1"
        asset_id = "my-custom-policy"
        version = "1.0.0"
        name = "My Custom Policy"

        schema_json = (
            '{"$schema": "http://json-schema.org/draft-07/schema#", "type": "object"}'
        )
        metadata_yaml = """#%Policy Definition 0.1
name: my_custom_policy
description: Test policy
category: Custom
"""

        response_body = {
            "publicationStatusLink": "https://anypoint.mulesoft.com/exchange/api/v2/organizations/org1/assets/org1/my-custom-policy/1.0.0/publication/status/abc123"
        }

        resp = make_response(
            status=202,
            json_body=response_body,
            url=f"{BASE}/exchange/api/v2/organizations/{org_id}/assets/{org_id}/{asset_id}/{version}",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        result = Exchange(http).create_policy_definition(
            org_id=org_id,
            asset_id=asset_id,
            version=version,
            name=name,
            schema_json=schema_json,
            metadata_yaml=metadata_yaml,
        )

        call = fake.calls[0]
        self.assertEqual(call["method"], "POST")
        self.assertEqual(
            call["url"],
            f"{BASE}/exchange/api/v2/organizations/{org_id}/assets/{org_id}/{asset_id}/{version}",
        )
        # Verify form data
        self.assertEqual(call["files"]["name"], (None, name))
        self.assertEqual(call["files"]["type"], (None, "policy"))
        self.assertEqual(call["files"]["status"], (None, "published"))
        # Verify header
        self.assertEqual(call["headers"]["x-sync-publication"], "false")
        self.assertIn("publicationStatusLink", result)

    def test_create_policy_definition_with_custom_group_id(self):
        """Test create_policy_definition with custom group_id"""
        org_id = "org1"
        group_id = "custom-group"
        asset_id = "my-policy"
        version = "1.0.0"

        resp = make_response(
            status=202,
            json_body={"publicationStatusLink": "..."},
            url=f"{BASE}/exchange/api/v2/organizations/{org_id}/assets/{group_id}/{asset_id}/{version}",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        Exchange(http).create_policy_definition(
            org_id=org_id,
            asset_id=asset_id,
            version=version,
            name="Test Policy",
            schema_json="{}",
            metadata_yaml="#%Policy Definition 0.1\nname: test",
            group_id=group_id,
        )

        call = fake.calls[0]
        self.assertIn(f"/assets/{group_id}/{asset_id}/{version}", call["url"])

    def test_create_policy_definition_sync_publication(self):
        """Test create_policy_definition with sync_publication=True"""
        org_id = "org1"

        resp = make_response(
            status=200,
            json_body={"status": "completed"},
            url=f"{BASE}/exchange/api/v2/organizations/{org_id}/assets/{org_id}/test-policy/1.0.0",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        Exchange(http).create_policy_definition(
            org_id=org_id,
            asset_id="test-policy",
            version="1.0.0",
            name="Test",
            schema_json="{}",
            metadata_yaml="#%Policy Definition 0.1\nname: test",
            sync_publication=True,
        )

        call = fake.calls[0]
        self.assertEqual(call["headers"]["x-sync-publication"], "true")

    def test_create_policy_implementation_success(self):
        """Test create_policy_implementation successfully creates an implementation asset"""
        import os
        import tempfile

        org_id = "org1"
        asset_id = "my-policy-imp"
        version = "1.0.0"
        name = "My Policy Implementation"
        policy_definition_gav = "org1:my-policy:1.0.0"

        implementation_yaml = """#%Policy Implementation 1.0
technology: mule4
minRuntimeVersion: 4.6.8
supportedJavaVersions:
  - "8"
  - "11"
"""

        # Create a temporary JAR file
        tmpdir = tempfile.mkdtemp()
        jar_path = os.path.join(tmpdir, "test-policy-1.0.0-mule-policy.jar")
        with open(jar_path, "wb") as f:
            f.write(b"PK\x03\x04")  # Minimal ZIP header

        response_body = {
            "publicationStatusLink": "https://anypoint.mulesoft.com/exchange/api/v2/organizations/org1/assets/org1/my-policy-imp/1.0.0/publication/status/xyz789"
        }

        resp = make_response(
            status=202,
            json_body=response_body,
            url=f"{BASE}/exchange/api/v2/organizations/{org_id}/assets/{org_id}/{asset_id}/{version}",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        try:
            result = Exchange(http).create_policy_implementation(
                org_id=org_id,
                asset_id=asset_id,
                version=version,
                name=name,
                policy_jar_path=jar_path,
                implementation_yaml=implementation_yaml,
                policy_definition_gav=policy_definition_gav,
            )

            call = fake.calls[0]
            self.assertEqual(call["method"], "POST")
            # Verify form data
            self.assertEqual(call["files"]["name"], (None, name))
            self.assertEqual(call["files"]["type"], (None, "policy-implementation"))
            self.assertEqual(call["files"]["status"], (None, "published"))
            self.assertEqual(
                call["files"]["dependencies"], (None, policy_definition_gav)
            )
            # Verify JAR file is included
            self.assertIn("files.binary.jar", call["files"])
            # Verify metadata YAML
            self.assertIn("files.metadata.yaml", call["files"])
            self.assertIn("publicationStatusLink", result)
        finally:
            os.unlink(jar_path)
            os.rmdir(tmpdir)

    def test_create_policy_implementation_file_not_found(self):
        """Test create_policy_implementation raises FileNotFoundError for missing JAR"""
        fake = FakeSession([])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        with self.assertRaises(FileNotFoundError) as ctx:
            Exchange(http).create_policy_implementation(
                org_id="org1",
                asset_id="my-policy-imp",
                version="1.0.0",
                name="Test",
                policy_jar_path="/nonexistent/policy.jar",
                implementation_yaml="#%Policy Implementation 1.0\ntechnology: mule4",
                policy_definition_gav="org1:my-policy:1.0.0",
            )
        self.assertIn("Policy JAR file not found", str(ctx.exception))

    def test_create_custom_policy_creates_both_assets(self):
        """Test create_custom_policy creates both definition and implementation"""
        import os
        import tempfile

        org_id = "org1"
        policy_asset_id = "my-custom-policy"
        version = "1.0.0"
        name = "My Custom Policy"
        description = "A test custom policy"
        schema_json = '{"type": "object"}'

        # Create a temporary JAR file
        tmpdir = tempfile.mkdtemp()
        jar_path = os.path.join(tmpdir, "my-policy-1.0.0-mule-policy.jar")
        with open(jar_path, "wb") as f:
            f.write(b"PK\x03\x04")

        # Response for policy definition
        def_resp = make_response(
            status=202,
            json_body={"publicationStatusLink": "...definition..."},
            url=f"{BASE}/exchange/api/v2/organizations/{org_id}/assets/{org_id}/{policy_asset_id}/{version}",
        )
        # Response for policy implementation
        impl_resp = make_response(
            status=202,
            json_body={"publicationStatusLink": "...implementation..."},
            url=f"{BASE}/exchange/api/v2/organizations/{org_id}/assets/{org_id}/{policy_asset_id}-imp/{version}",
        )
        fake = FakeSession([def_resp, impl_resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        try:
            result = Exchange(http).create_custom_policy(
                org_id=org_id,
                policy_asset_id=policy_asset_id,
                version=version,
                name=name,
                description=description,
                schema_json=schema_json,
                policy_jar_path=jar_path,
            )

            # Verify two calls were made
            self.assertEqual(len(fake.calls), 2)

            # First call: policy definition
            def_call = fake.calls[0]
            self.assertEqual(def_call["files"]["type"], (None, "policy"))
            self.assertIn(
                f"/assets/{org_id}/{policy_asset_id}/{version}", def_call["url"]
            )

            # Second call: policy implementation
            impl_call = fake.calls[1]
            self.assertEqual(
                impl_call["files"]["type"], (None, "policy-implementation")
            )
            self.assertIn(
                f"/assets/{org_id}/{policy_asset_id}-imp/{version}", impl_call["url"]
            )
            # Verify dependency GAV
            self.assertEqual(
                impl_call["files"]["dependencies"],
                (None, f"{org_id}:{policy_asset_id}:{version}"),
            )

            # Verify result structure
            self.assertIn("definition", result)
            self.assertIn("implementation", result)
        finally:
            os.unlink(jar_path)
            os.rmdir(tmpdir)

    def test_create_custom_policy_with_custom_options(self):
        """Test create_custom_policy with custom category and technology options"""
        import os
        import tempfile

        org_id = "org1"
        policy_asset_id = "security-policy"
        version = "2.0.0"

        tmpdir = tempfile.mkdtemp()
        jar_path = os.path.join(tmpdir, "security-policy.jar")
        with open(jar_path, "wb") as f:
            f.write(b"PK\x03\x04")

        def_resp = make_response(
            status=202,
            json_body={},
            url=f"{BASE}/exchange/api/v2/organizations/{org_id}/assets/{org_id}/{policy_asset_id}/{version}",
        )
        impl_resp = make_response(
            status=202,
            json_body={},
            url=f"{BASE}/exchange/api/v2/organizations/{org_id}/assets/{org_id}/{policy_asset_id}-imp/{version}",
        )
        fake = FakeSession([def_resp, impl_resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        try:
            Exchange(http).create_custom_policy(
                org_id=org_id,
                policy_asset_id=policy_asset_id,
                version=version,
                name="Security Policy",
                description="Custom security policy",
                schema_json="{}",
                policy_jar_path=jar_path,
                category="Security",
                violation_category="security",
                technology="mule4",
                min_runtime_version="4.5.0",
                supported_java_versions=["11", "17"],
            )

            # Verify the metadata YAML in the definition call
            def_call = fake.calls[0]
            metadata_tuple = def_call["files"]["files.metadata.yaml"]
            metadata_content = metadata_tuple[1].decode("utf-8")
            self.assertIn("category: Security", metadata_content)
            self.assertIn("violationCategory: security", metadata_content)

            # Verify implementation YAML
            impl_call = fake.calls[1]
            impl_metadata_tuple = impl_call["files"]["files.metadata.yaml"]
            impl_content = impl_metadata_tuple[1].decode("utf-8")
            self.assertIn("minRuntimeVersion: 4.5.0", impl_content)
            self.assertIn('"11"', impl_content)
            self.assertIn('"17"', impl_content)
        finally:
            os.unlink(jar_path)
            os.rmdir(tmpdir)

    def test_list_policy_assets_all_policies(self):
        """Test list_policy_assets returns all policy assets"""
        mulesoft_group = "68ef9520-24e9-4cf2-b2f5-620025690913"
        org_id = "my-org-123"

        assets_payload = [
            {
                "groupId": mulesoft_group,
                "assetId": "rate-limiting",
                "version": "1.0.0",
                "type": "policy",
            },
            {
                "groupId": mulesoft_group,
                "assetId": "cors",
                "version": "1.0.0",
                "type": "policy",
            },
            {
                "groupId": org_id,
                "assetId": "my-custom-policy",
                "version": "1.0.0",
                "type": "policy",
            },
            {
                "groupId": org_id,
                "assetId": "my-policy-imp",
                "version": "1.0.0",
                "type": "policy-implementation",
            },
            {
                "groupId": org_id,
                "assetId": "my-api",
                "version": "1.0.0",
                "type": "rest-api",
            },
        ]

        resp = make_response(
            status=200,
            json_body=assets_payload,
            url=f"{BASE}/exchange/api/v2/assets",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        result = Exchange(http).list_policy_assets()

        # Should only return type="policy" assets
        self.assertEqual(len(result), 3)
        asset_ids = {a["assetId"] for a in result}
        self.assertEqual(asset_ids, {"rate-limiting", "cors", "my-custom-policy"})

        # Verify search param was used
        call = fake.calls[0]
        self.assertEqual(call["params"]["search"], "policy")

    def test_list_policy_assets_org_only(self):
        """Test list_policy_assets with org_id and include_mulesoft_policies=False"""
        org_id = "my-org-123"

        assets_payload = [
            {
                "groupId": org_id,
                "assetId": "my-custom-policy",
                "version": "1.0.0",
                "type": "policy",
            },
            {
                "groupId": org_id,
                "assetId": "my-policy-imp",
                "version": "1.0.0",
                "type": "policy-implementation",
            },
        ]

        resp = make_response(
            status=200,
            json_body=assets_payload,
            url=f"{BASE}/exchange/api/v2/assets",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        result = Exchange(http).list_policy_assets(
            org_id=org_id, include_mulesoft_policies=False
        )

        # Should only return policy definition
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["assetId"], "my-custom-policy")

        # Verify organizationId param was used (not search)
        call = fake.calls[0]
        self.assertEqual(call["params"]["organizationId"], org_id)
        self.assertNotIn("search", call["params"])

    def test_list_policy_assets_org_with_mulesoft(self):
        """Test list_policy_assets with org_id and include_mulesoft_policies=True (default)"""
        mulesoft_group = "68ef9520-24e9-4cf2-b2f5-620025690913"
        org_id = "my-org-123"
        other_org = "other-org-456"

        assets_payload = [
            {
                "groupId": mulesoft_group,
                "assetId": "rate-limiting",
                "version": "1.0.0",
                "type": "policy",
            },
            {
                "groupId": org_id,
                "assetId": "my-custom-policy",
                "version": "1.0.0",
                "type": "policy",
            },
            {
                "groupId": other_org,
                "assetId": "other-policy",
                "version": "1.0.0",
                "type": "policy",
            },
        ]

        resp = make_response(
            status=200,
            json_body=assets_payload,
            url=f"{BASE}/exchange/api/v2/assets",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        result = Exchange(http).list_policy_assets(org_id=org_id)

        # Should include MuleSoft policies and org policies, but not other-org policies
        self.assertEqual(len(result), 2)
        asset_ids = {a["assetId"] for a in result}
        self.assertEqual(asset_ids, {"rate-limiting", "my-custom-policy"})

    def test_list_policy_assets_empty_response(self):
        """Test list_policy_assets handles empty response"""
        resp = make_response(
            status=200,
            json_body=[],
            url=f"{BASE}/exchange/api/v2/assets",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        result = Exchange(http).list_policy_assets()
        self.assertEqual(result, [])

    def test_list_policy_assets_filters_non_dict(self):
        """Test list_policy_assets filters out non-dict entries"""
        assets_payload = [
            {
                "groupId": "org1",
                "assetId": "my-policy",
                "version": "1.0.0",
                "type": "policy",
            },
            "not-a-dict",
            None,
            123,
        ]

        resp = make_response(
            status=200,
            json_body=assets_payload,
            url=f"{BASE}/exchange/api/v2/assets",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        result = Exchange(http).list_policy_assets()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["assetId"], "my-policy")

    def test_list_policy_implementations_all(self):
        """Test list_policy_implementations returns all implementation assets"""
        mulesoft_group = "68ef9520-24e9-4cf2-b2f5-620025690913"
        org_id = "my-org-123"

        assets_payload = [
            {
                "groupId": mulesoft_group,
                "assetId": "rate-limiting-flex",
                "version": "1.0.0",
                "type": "policy-implementation",
            },
            {
                "groupId": org_id,
                "assetId": "my-policy-imp",
                "version": "1.0.0",
                "type": "policy-implementation",
            },
            {
                "groupId": org_id,
                "assetId": "my-custom-policy",
                "version": "1.0.0",
                "type": "policy",
            },
        ]

        resp = make_response(
            status=200,
            json_body=assets_payload,
            url=f"{BASE}/exchange/api/v2/assets",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        result = Exchange(http).list_policy_implementations()

        # Should only return type="policy-implementation" assets
        self.assertEqual(len(result), 2)
        asset_ids = {a["assetId"] for a in result}
        self.assertEqual(asset_ids, {"rate-limiting-flex", "my-policy-imp"})

    def test_list_policy_implementations_org_only(self):
        """Test list_policy_implementations with org_id and include_mulesoft_policies=False"""
        org_id = "my-org-123"

        assets_payload = [
            {
                "groupId": org_id,
                "assetId": "my-policy-imp",
                "version": "1.0.0",
                "type": "policy-implementation",
            },
        ]

        resp = make_response(
            status=200,
            json_body=assets_payload,
            url=f"{BASE}/exchange/api/v2/assets",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        result = Exchange(http).list_policy_implementations(
            org_id=org_id, include_mulesoft_policies=False
        )

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["assetId"], "my-policy-imp")

        # Verify organizationId param was used
        call = fake.calls[0]
        self.assertEqual(call["params"]["organizationId"], org_id)

    def test_list_policy_implementations_org_with_mulesoft(self):
        """Test list_policy_implementations includes both org and MuleSoft policies"""
        mulesoft_group = "68ef9520-24e9-4cf2-b2f5-620025690913"
        org_id = "my-org-123"
        other_org = "other-org-456"

        assets_payload = [
            {
                "groupId": mulesoft_group,
                "assetId": "cors-flex",
                "version": "1.0.0",
                "type": "policy-implementation",
            },
            {
                "groupId": org_id,
                "assetId": "my-policy-imp",
                "version": "1.0.0",
                "type": "policy-implementation",
            },
            {
                "groupId": other_org,
                "assetId": "other-imp",
                "version": "1.0.0",
                "type": "policy-implementation",
            },
        ]

        resp = make_response(
            status=200,
            json_body=assets_payload,
            url=f"{BASE}/exchange/api/v2/assets",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        result = Exchange(http).list_policy_implementations(org_id=org_id)

        # Should include MuleSoft and org implementations, but not other-org
        self.assertEqual(len(result), 2)
        asset_ids = {a["assetId"] for a in result}
        self.assertEqual(asset_ids, {"cors-flex", "my-policy-imp"})

    def test_get_asset_with_version(self):
        """Test get_asset retrieves a specific asset version"""
        group_id = "org1"
        asset_id = "my-api"
        version = "1.0.0"

        asset_payload = {
            "groupId": group_id,
            "assetId": asset_id,
            "version": version,
            "name": "My API",
            "type": "rest-api",
            "files": [
                {"classifier": "raml", "packaging": "zip", "mainFile": "api.raml"},
            ],
        }

        resp = make_response(
            status=200,
            json_body=asset_payload,
            url=f"{BASE}/exchange/api/v2/assets/{group_id}/{asset_id}/{version}",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        result = Exchange(http).get_asset(group_id, asset_id, version)

        call = fake.calls[0]
        self.assertEqual(call["method"], "GET")
        self.assertEqual(
            call["url"],
            f"{BASE}/exchange/api/v2/assets/{group_id}/{asset_id}/{version}",
        )
        self.assertEqual(result, asset_payload)
        self.assertEqual(result["name"], "My API")
        self.assertIn("files", result)

    def test_get_asset_without_version(self):
        """Test get_asset retrieves latest version when version not specified"""
        group_id = "org1"
        asset_id = "my-api"

        asset_payload = {
            "groupId": group_id,
            "assetId": asset_id,
            "version": "2.0.0",
            "name": "My API",
        }

        resp = make_response(
            status=200,
            json_body=asset_payload,
            url=f"{BASE}/exchange/api/v2/assets/{group_id}/{asset_id}",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        result = Exchange(http).get_asset(group_id, asset_id)

        call = fake.calls[0]
        self.assertEqual(
            call["url"],
            f"{BASE}/exchange/api/v2/assets/{group_id}/{asset_id}",
        )
        self.assertEqual(result["version"], "2.0.0")

    def test_get_asset_not_found(self):
        """Test get_asset raises HttpError for missing asset"""
        group_id = "org1"
        asset_id = "nonexistent-api"

        resp = make_response(
            status=404,
            text="Asset not found",
            url=f"{BASE}/exchange/api/v2/assets/{group_id}/{asset_id}",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        with self.assertRaises(HttpError) as ctx:
            Exchange(http).get_asset(group_id, asset_id)

        self.assertEqual(ctx.exception.status, 404)

    def test_get_asset_empty_response(self):
        """Test get_asset handles empty response"""
        group_id = "org1"
        asset_id = "my-api"

        resp = make_response(
            status=200,
            text="",
            url=f"{BASE}/exchange/api/v2/assets/{group_id}/{asset_id}",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        result = Exchange(http).get_asset(group_id, asset_id)
        self.assertEqual(result, {})


if __name__ == "__main__":
    unittest.main()
