# tests/test_organizations_accessible.py
import unittest

from anypoint_sdk._http import HttpClient
from anypoint_sdk.resources.organizations import Organizations
from tests.fakes import FakeSession
from tests.helpers import make_response

BASE = "https://api.test.local"


class OrganizationsAccessibleTests(unittest.TestCase):
    def test_list_accessible_normalises_and_dedupes(self):
        me_payload = {
            "user": {
                "organization": {
                    "id": "root-1",
                    "name": "DNF",
                    "isRoot": True,
                    "isMaster": True,
                    "parentOrganizationIds": [],
                }
            },
            "memberOfOrganizations": [
                {
                    "id": "root-1",
                    "name": "DNF",
                    "isRoot": True,
                    "isMaster": True,
                    "parentOrganizationIds": [],
                },
                {
                    "id": "sub-1",
                    "name": "mobile",
                    "parentId": "root-1",
                    "isRoot": False,
                    "isMaster": False,
                },
            ],
            "contributorOfOrganizations": [
                {
                    "id": "sub-2",
                    "name": "mortgages",
                    "parentId": "root-1",
                    "isRoot": False,
                    "isMaster": False,
                },
                # duplicate to prove dedupe
                {
                    "id": "sub-1",
                    "name": "mobile",
                    "parentId": "root-1",
                    "isRoot": False,
                    "isMaster": False,
                },
            ],
        }

        resp = make_response(
            status=200, json_body=me_payload, url=f"{BASE}/accounts/api/me"
        )
        http = HttpClient(base_url=BASE, session=FakeSession([resp]), retries=0)

        orgs = Organizations(http).list_accessible()

        self.assertEqual(len(orgs), 3)
        ids = {o["id"] for o in orgs}
        self.assertSetEqual(ids, {"root-1", "sub-1", "sub-2"})

        root = next(o for o in orgs if o["id"] == "root-1")
        self.assertTrue(root.get("isRoot"))
        self.assertTrue(root.get("isMaster"))
        self.assertIsNone(root.get("parentId"))

    def test_parent_falls_back_to_parentOrganizationIds(self):
        me_payload = {
            "user": {
                "organization": {
                    "id": "root-1",
                    "name": "DNF",
                    "isRoot": True,
                    "isMaster": True,
                }
            },
            "memberOfOrganizations": [
                {
                    "id": "child-1",
                    "name": "child",
                    "parentOrganizationIds": ["root-1"],
                    "isRoot": False,
                    "isMaster": False,
                }
            ],
            "contributorOfOrganizations": [],
        }
        resp = make_response(
            status=200, json_body=me_payload, url=f"{BASE}/accounts/api/me"
        )
        http = HttpClient(base_url=BASE, session=FakeSession([resp]), retries=0)

        orgs = Organizations(http).list_accessible()
        child = next(o for o in orgs if o["id"] == "child-1")
        self.assertEqual(child.get("parentId"), "root-1")

    def test_list_accessible_nested_arrays_also_supported(self):
        me_payload = {
            "user": {
                "organization": {
                    "id": "root-1",
                    "name": "DNF",
                    "isRoot": True,
                    "isMaster": True,
                },
                "memberOfOrganizations": [
                    {
                        "id": "sub-1",
                        "name": "mobile",
                        "parentId": "root-1",
                        "isRoot": False,
                        "isMaster": False,
                    }
                ],
                "contributorOfOrganizations": [
                    {
                        "id": "sub-2",
                        "name": "mortgages",
                        "parentId": "root-1",
                        "isRoot": False,
                        "isMaster": False,
                    }
                ],
            }
        }
        resp = make_response(
            status=200, json_body=me_payload, url=f"{BASE}/accounts/api/me"
        )
        http = HttpClient(base_url=BASE, session=FakeSession([resp]), retries=0)

        orgs = Organizations(http).list_accessible()
        ids = {o["id"] for o in orgs}
        self.assertSetEqual(ids, {"root-1", "sub-1", "sub-2"})

    def test_list_accessible_when_no_primary_org(self):
        me_payload = {
            "user": {},
            "memberOfOrganizations": [],
            "contributorOfOrganizations": [],
        }
        resp = make_response(
            status=200, json_body=me_payload, url=f"{BASE}/accounts/api/me"
        )
        http = HttpClient(base_url=BASE, session=FakeSession([resp]), retries=0)

        orgs = Organizations(http).list_accessible()
        self.assertEqual(orgs, [])  # nothing collected

    def test_members_ignores_non_dict_entries(self):
        me_payload = {
            "user": {"organization": {"id": "root-1", "name": "DNF"}},
            "memberOfOrganizations": [
                {"id": "sub-1", "name": "mobile"},  # dict, will be included
                "not-a-dict",  # non-dict, should be ignored
            ],
            "contributorOfOrganizations": [],
        }
        resp = make_response(
            status=200, json_body=me_payload, url=f"{BASE}/accounts/api/me"
        )
        http = HttpClient(base_url=BASE, session=FakeSession([resp]), retries=0)

        orgs = Organizations(http).list_accessible()
        ids = {o["id"] for o in orgs}
        self.assertSetEqual(ids, {"root-1", "sub-1"})

    def test_contributors_empty_list(self):
        me_payload = {
            "user": {"organization": {"id": "root-1", "name": "DNF"}},
            "memberOfOrganizations": [],
            "contributorOfOrganizations": [],  # zero-iteration
        }
        resp = make_response(
            status=200, json_body=me_payload, url=f"{BASE}/accounts/api/me"
        )
        http = HttpClient(base_url=BASE, session=FakeSession([resp]), retries=0)

        orgs = Organizations(http).list_accessible()
        self.assertEqual(len(orgs), 1)  # only primary org

    def test_contributors_ignores_non_dict_and_handles_multiple_items(self):
        me_payload = {
            "user": {"organization": {"id": "root-1", "name": "DNF"}},
            # no members to keep it focused
            "memberOfOrganizations": [],
            # one valid dict and one non-dict to exercise both True and False paths
            "contributorOfOrganizations": [
                {
                    "id": "sub-2",
                    "name": "mortgages",
                    "parentId": "root-1",
                    "isRoot": False,
                    "isMaster": False,
                },
                "not-a-dict",
            ],
        }
        resp = make_response(
            status=200, json_body=me_payload, url=f"{BASE}/accounts/api/me"
        )
        http = HttpClient(base_url=BASE, session=FakeSession([resp]), retries=0)

        orgs = Organizations(http).list_accessible()

        # Only the dict contributor should be included alongside the primary org
        ids = {o["id"] for o in orgs}
        self.assertSetEqual(ids, {"root-1", "sub-2"})


if __name__ == "__main__":
    unittest.main()
