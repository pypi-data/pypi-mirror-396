# tests/test_groups.py
import unittest
from unittest.mock import patch

from anypoint_sdk._http import HttpClient
from anypoint_sdk.resources.groups import GroupInstances
from tests.fakes import FakeSession
from tests.helpers import make_response

BASE = "https://api.test.local"


class GroupInstancesTests(unittest.TestCase):
    def test_list_normalises_and_dedupes(self):
        org_id = "o1"
        env_id = "e1"
        payload = {
            "total": 2,
            "instances": [
                {
                    "id": 368690,
                    "groupName": "rate-limit-group",
                    "groupVersionName": "v1",
                    "status": "PRIVATE",
                    "deprecated": False,
                    "environmentId": env_id,
                    "apiInstances": [{"id": 20473240}],
                },
                # duplicate id to prove dedupe
                {"id": 368690, "groupName": "rate-limit-group"},
                # non dict ignored
                "bad",
            ],
        }
        resp = make_response(
            status=200,
            json_body=payload,
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/groupInstances",
        )
        http = HttpClient(base_url=BASE, session=FakeSession([resp]), retries=0)

        out = GroupInstances(http).list(org_id, env_id)
        self.assertEqual(len(out), 1)
        g = out[0]
        self.assertEqual(g["id"], 368690)
        self.assertEqual(g["groupName"], "rate-limit-group")
        self.assertEqual(g["groupVersionName"], "v1")
        self.assertEqual(g["environmentId"], env_id)
        self.assertEqual(g["apiInstanceIds"], [20473240])

    def test_list_handles_missing_or_wrong_shape(self):
        org_id = "o1"
        env_id = "e1"
        resp = make_response(
            status=200,
            json_body={"total": 0},  # no "instances" key
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/groupInstances",
        )
        http = HttpClient(base_url=BASE, session=FakeSession([resp]), retries=0)
        out = GroupInstances(http).list(org_id, env_id)
        self.assertEqual(out, [])

    def test_get_returns_detail(self):
        org_id = "o1"
        env_id = "e1"
        gid = 368690
        detail = {
            "id": gid,
            "groupVersionName": "v1",
            "apiInstances": [{"id": 20473240}],
        }
        resp = make_response(
            status=200,
            json_body=detail,
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/groupInstances/{gid}",
        )
        http = HttpClient(base_url=BASE, session=FakeSession([resp]), retries=0)

        got = GroupInstances(http).get(org_id, env_id, gid)
        self.assertEqual(got["id"], gid)
        self.assertEqual(got["groupVersionName"], "v1")

    def test_find_group_for_api_matches_from_list_payload_without_detail_fetch(self):
        org_id = "o1"
        env_id = "e1"
        api_id = 20473240
        # List payload already includes apiInstances with the target id
        payload = {
            "instances": [
                {"id": 111, "apiInstances": []},
                {"id": 222, "apiInstances": [{"id": api_id}]},
            ]
        }
        list_resp = make_response(
            status=200,
            json_body=payload,
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/groupInstances",
        )
        fake = FakeSession([list_resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        gid = GroupInstances(http).find_group_for_api(org_id, env_id, api_id)
        self.assertEqual(gid, 222)
        # Only one call, no detail fetch needed
        self.assertEqual(len(fake.calls), 1)

    def test_find_group_for_api_fetches_detail_if_list_inconclusive(self):
        org_id = "o1"
        env_id = "e1"
        api_id = 20473240
        # List with no apiInstances shapes
        list_payload = {"instances": [{"id": 111}, {"id": 222}]}
        list_resp = make_response(
            status=200,
            json_body=list_payload,
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/groupInstances",
        )
        # First detail does not contain the API
        detail_111 = make_response(
            status=200,
            json_body={"id": 111, "apiInstances": []},
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/groupInstances/111",
        )
        # Second detail matches
        detail_222 = make_response(
            status=200,
            json_body={"id": 222, "apiInstances": [{"id": api_id}]},
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/groupInstances/222",
        )

        fake = FakeSession([list_resp, detail_111, detail_222])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        gid = GroupInstances(http).find_group_for_api(org_id, env_id, api_id)
        self.assertEqual(gid, 222)
        # list + two details
        self.assertEqual(len(fake.calls), 3)

    def test_find_group_for_api_returns_none_when_not_found(self):
        org_id = "o1"
        env_id = "e1"
        api_id = 20473240
        list_payload = {"instances": [{"id": 111}, {"id": 222}]}
        list_resp = make_response(
            status=200,
            json_body=list_payload,
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/groupInstances",
        )
        detail_111 = make_response(
            status=200,
            json_body={"id": 111, "apiInstances": []},
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/groupInstances/111",
        )
        detail_222 = make_response(
            status=200,
            json_body={"id": 222, "apiInstances": [{"id": 12345}]},  # not our api_id
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/groupInstances/222",
        )

        fake = FakeSession([list_resp, detail_111, detail_222])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        gid = GroupInstances(http).find_group_for_api(org_id, env_id, api_id)
        self.assertIsNone(gid)

    def test_extract_api_ids_accepts_ints_or_dicts(self):
        org_id = "o1"
        env_id = "e1"
        payload = {
            "instances": [
                {"id": 1, "apiInstances": [10, 11, {"id": 12}, {"oops": 13}, "bad"]},
            ]
        }
        resp = make_response(
            status=200,
            json_body=payload,
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/groupInstances",
        )
        http = HttpClient(base_url=BASE, session=FakeSession([resp]), retries=0)
        out = GroupInstances(http).list(org_id, env_id)
        self.assertEqual(out[0]["apiInstanceIds"], [10, 11, 12])

    def test_extract_api_ids_skips_unparsable_ids(self):
        org_id = "o1"
        env_id = "e1"
        # First apiInstances element will raise ValueError on int("abc") and hit the except path,
        # the remaining ones should be parsed and kept.
        payload = {
            "instances": [
                {
                    "id": 1,
                    "apiInstances": [
                        {"id": "abc"},  # triggers the except branch
                        {"id": "5"},  # valid string int
                        7,  # raw int supported
                    ],
                }
            ]
        }
        resp = make_response(
            status=200,
            json_body=payload,
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/groupInstances",
        )
        http = HttpClient(base_url=BASE, session=FakeSession([resp]), retries=0)

        out = GroupInstances(http).list(org_id, env_id)

        # The unparsable id is skipped, the others remain
        self.assertEqual(out[0]["apiInstanceIds"], [5, 7])

    def test_find_group_for_api_skips_entries_with_no_id(self):
        org_id = "o1"
        env_id = "e1"
        api_id = 12345

        # List includes one entry without an id (becomes id=0 after normalisation),
        # and one valid entry that will not match our api_id.
        list_payload = {
            "instances": [
                {
                    "groupName": "no-id-here"
                },  # id missing, will normalise to 0, triggers 'continue'
                {"id": 222},  # valid id, but no apiInstances here
            ]
        }
        list_resp = make_response(
            status=200,
            json_body=list_payload,
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/groupInstances",
        )
        # Detail for 222 that does not contain our api_id, ensures overall result is None
        detail_222 = make_response(
            status=200,
            json_body={"id": 222, "apiInstances": [{"id": 99999}]},
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/groupInstances/222",
        )

        fake = FakeSession([list_resp, detail_222])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        gid = GroupInstances(http).find_group_for_api(org_id, env_id, api_id)

        # Not found, and we should have only fetched detail for 222, not for the missing id entry
        self.assertIsNone(gid)
        self.assertEqual(len(fake.calls), 2)
        self.assertIn("/groupInstances/222", fake.calls[1]["url"])
        # There must not be a call for an id of 0
        self.assertFalse(any("/groupInstances/0" in c["url"] for c in fake.calls))

    def test_find_group_for_api_skips_entry_with_falsy_id(self):
        org_id = "o1"
        env_id = "e1"
        api_id = 12345

        # Detail for the only valid group id
        detail_222 = make_response(
            status=200,
            json_body={"id": 222, "apiInstances": [{"id": 99999}]},  # not our api_id
            url=f"{BASE}/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/groupInstances/222",
        )
        fake = FakeSession([detail_222])
        http = HttpClient(base_url=BASE, session=fake, retries=0)
        gi = GroupInstances(http)

        # Patch list() to include a first entry with a falsy id to trigger the `continue`
        with patch.object(
            GroupInstances,
            "list",
            return_value=[
                {"id": 0, "apiInstanceIds": []},
                {"id": 222, "apiInstanceIds": []},
            ],
        ):
            result = gi.find_group_for_api(org_id, env_id, api_id)

        self.assertIsNone(result)
        # Only one detail fetch for id 222, the falsy id was skipped
        self.assertEqual(len(fake.calls), 1)
        self.assertIn("/groupInstances/222", fake.calls[0]["url"])


if __name__ == "__main__":
    unittest.main()
