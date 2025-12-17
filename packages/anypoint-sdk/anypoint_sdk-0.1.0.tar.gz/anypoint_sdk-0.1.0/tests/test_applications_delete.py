import unittest

from anypoint_sdk._http import HttpClient, HttpError
from anypoint_sdk.resources.applications import Applications
from tests.fakes import FakeSession
from tests.helpers import make_response

BASE = "https://api.test.local"


class ApplicationsDeleteTests(unittest.TestCase):
    def test_delete_application_success(self):
        org_id = "o1"
        app_id = 12345

        resp = make_response(
            status=204,
            text="",
            url=f"{BASE}/apiplatform/repository/v2/organizations/{org_id}/applications/{app_id}",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        result = Applications(http).delete(org_id, app_id)

        self.assertIsNone(result)
        self.assertEqual(len(fake.calls), 1)
        call = fake.calls[0]
        self.assertEqual(call["method"], "DELETE")
        self.assertEqual(
            call["url"],
            f"{BASE}/apiplatform/repository/v2/organizations/{org_id}/applications/{app_id}",
        )

    def test_delete_application_with_string_id(self):
        org_id = "o1"
        app_id = "app-123"

        resp = make_response(
            status=204,
            text="",
            url=f"{BASE}/apiplatform/repository/v2/organizations/{org_id}/applications/{app_id}",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        Applications(http).delete(org_id, app_id)

        call = fake.calls[0]
        self.assertEqual(
            call["url"],
            f"{BASE}/apiplatform/repository/v2/organizations/{org_id}/applications/{app_id}",
        )

    def test_delete_application_handles_404_not_found(self):
        org_id = "o1"
        app_id = 99999

        resp = make_response(
            status=404,
            text="Not Found",
            url=f"{BASE}/apiplatform/repository/v2/organizations/{org_id}/applications/{app_id}",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        with self.assertRaises(HttpError) as ctx:
            Applications(http).delete(org_id, app_id)

        self.assertEqual(ctx.exception.status, 404)

    def test_delete_application_handles_403_forbidden(self):
        org_id = "o1"
        app_id = 12345

        resp = make_response(
            status=403,
            text="Forbidden",
            url=f"{BASE}/apiplatform/repository/v2/organizations/{org_id}/applications/{app_id}",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        with self.assertRaises(HttpError) as ctx:
            Applications(http).delete(org_id, app_id)

        self.assertEqual(ctx.exception.status, 403)

    def test_delete_application_handles_200_response(self):
        """Some APIs return 200 instead of 204 for successful deletion"""
        org_id = "o1"
        app_id = 12345

        resp = make_response(
            status=200,
            json_body={"message": "Application deleted successfully"},
            url=f"{BASE}/apiplatform/repository/v2/organizations/{org_id}/applications/{app_id}",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        result = Applications(http).delete(org_id, app_id)
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
