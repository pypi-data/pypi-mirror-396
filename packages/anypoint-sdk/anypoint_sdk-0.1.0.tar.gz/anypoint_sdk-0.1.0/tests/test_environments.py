# tests/test_environments.py
import unittest

from anypoint_sdk._http import HttpClient, HttpError
from anypoint_sdk.resources.environments import Environments, EnvSummary, _dedupe
from tests.fakes import FakeSession
from tests.helpers import make_response

BASE = "https://api.test.local"


class _ListLogger:
    """Simple in-memory logger that fits LoggerLike for tests."""

    def __init__(self, name: str = "test") -> None:
        self.name = name
        self.records: list[tuple[str, str]] = []

    def debug(self, msg: str, *a, **kw) -> None:
        self.records.append(("DEBUG", msg % a if a else msg))

    def info(self, msg: str, *a, **kw) -> None:
        self.records.append(("INFO", msg % a if a else msg))

    def warning(self, msg: str, *a, **kw) -> None:
        self.records.append(("WARNING", msg % a if a else msg))

    def error(self, msg: str, *a, **kw) -> None:
        self.records.append(("ERROR", msg % a if a else msg))

    def child(self, suffix: str) -> "_ListLogger":
        return self


class EnvironmentsEdgeTests(unittest.TestCase):
    def test_empty_iterable_returns_empty_list(self):
        out = _dedupe([])
        self.assertEqual(out, [])

    def test_preserves_first_occurrence_and_order(self):
        a = EnvSummary(id="1", name="org-1")
        b = EnvSummary(id="2", name="org-2")
        c = EnvSummary(id="1", name="org-1")  # duplicate id, should be dropped
        d = EnvSummary(id="3", name="org-3")
        e = EnvSummary(id="2", name="org-2")  # duplicate id, should be dropped

        out = _dedupe([a, b, c, d, e])

        self.assertEqual([x.id for x in out], ["1", "2", "3"])
        self.assertIs(out[0], a)
        self.assertIs(out[1], b)
        self.assertIs(out[2], d)

    def test_skips_items_with_falsy_id(self):
        # Entries with empty or None id are ignored entirely
        a = EnvSummary(id="", name="org-1")
        b = EnvSummary(id=None, name="org-1")  # type: ignore[arg-type]
        c = EnvSummary(id="ok", name="org-2")

        out = _dedupe([a, b, c])

        self.assertEqual([x.id for x in out], ["ok"])
        self.assertIs(out[0], c)

    def test_accepts_any_iterable_not_just_lists(self):
        seq = [
            EnvSummary(id="1", name="org-1"),
            EnvSummary(id="1", name="org-1"),
            EnvSummary(id="2", name="org-2"),
        ]
        gen = (x for x in seq)  # generator, still an Iterable

        out = _dedupe(gen)

        self.assertEqual([x.id for x in out], ["1", "2"])

    def test_same_id_different_payload_keeps_first_object(self):
        first = EnvSummary(id="X", name="org-X")
        second = EnvSummary(id="X", name="org-X")  # different instance, same id

        out = _dedupe([first, second])

        self.assertEqual(len(out), 1)
        self.assertIs(out[0], first)

    def test_list_returns_from_cache_without_http_call(self):
        # Prepare an HttpClient that would error if used, to prove cache path returns early
        http = HttpClient(base_url=BASE, session=FakeSession([]), retries=0)
        envs_api = Environments(http)

        # Seed cache directly
        envs_api._cache["org-1"] = [EnvSummary(id="e1", name="Prod", type="production")]

        out = envs_api.list("org-1")  # should not touch HTTP
        self.assertEqual(
            out, [{"id": "e1", "name": "Prod", "type": "production", "region": None}]
        )

        # No calls made
        self.assertEqual(getattr(http._session, "scripted", []), [])  # type: ignore[attr-defined]

    def test_list_handles_dict_wrapper_with_data_none(self):
        org_id = "org-2"
        payload = {"data": None}
        resp = make_response(
            status=200,
            json_body=payload,
            url=f"{BASE}/accounts/api/organizations/{org_id}/environments",
        )
        http = HttpClient(base_url=BASE, session=FakeSession([resp]), retries=0)

        envs = Environments(http).list(org_id)
        self.assertEqual(envs, [])  # safely handled

    def test_list_ignores_non_dict_items(self):
        org_id = "org-3"
        payload = {
            "data": [{"id": "e1", "name": "Prod", "type": "production"}, "not-a-dict"]
        }
        resp = make_response(
            status=200,
            json_body=payload,
            url=f"{BASE}/accounts/api/organizations/{org_id}/environments",
        )
        http = HttpClient(base_url=BASE, session=FakeSession([resp]), retries=0)

        envs = Environments(http).list(org_id)
        self.assertEqual(len(envs), 1)
        self.assertEqual(envs[0]["id"], "e1")

    def test_list_by_orgs_skips_empty_id_and_404_and_logs(self):
        # orgs contain an empty id, plus one 404 and one OK
        orgs = [{"id": ""}, {"id": "o404"}, {"id": "o2"}]
        r404 = make_response(
            status=404,
            text="Not found",
            url=f"{BASE}/accounts/api/organizations/o404/environments",
        )
        ok = make_response(
            status=200,
            json_body={"data": [{"id": "e2", "name": "SB", "type": "sandbox"}]},
            url=f"{BASE}/accounts/api/organizations/o2/environments",
        )

        fake = FakeSession([r404, ok])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        log = _ListLogger("scanner")
        envs_api = Environments(http, logger=log)
        out = envs_api.list_by_orgs(orgs, use_cache=False)

        # Only o2 should be present
        self.assertEqual(set(out.keys()), {"o2"})
        self.assertEqual(out["o2"][0]["id"], "e2")

        # Warning logged for 404
        self.assertTrue(
            any(level == "WARNING" and "skipping" in msg for level, msg in log.records)
        )

    def test_list_by_orgs_erros_on_500_and_logs(self):
        orgs = [{"id": ""}, {"id": "o500"}, {"id": "o2"}]
        r500 = make_response(
            status=500,
            text="Server Error",
            url=f"{BASE}/accounts/api/organizations/o500/environments",
        )

        fake = FakeSession([r500])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        log = _ListLogger("scanner")
        envs_api = Environments(http, logger=log)
        with self.assertRaises(HttpError):
            envs_api.list_by_orgs(orgs, use_cache=False)

    def test_clear_cache_forces_next_call_to_hit_http(self):
        org_id = "org-4"
        p = {"data": [{"id": "e1", "name": "Prod", "type": "production"}]}
        resp1 = make_response(
            status=200,
            json_body=p,
            url=f"{BASE}/accounts/api/organizations/{org_id}/environments",
        )
        resp2 = make_response(
            status=200,
            json_body=p,
            url=f"{BASE}/accounts/api/organizations/{org_id}/environments",
        )
        fake = FakeSession([resp1, resp2])
        http = HttpClient(base_url=BASE, session=fake, retries=0)

        api = Environments(http)
        _ = api.list(org_id)  # populate cache
        api.clear_cache()
        _ = api.list(org_id)  # should use second scripted response

        # Two HTTP calls should have been recorded
        self.assertEqual(len(fake.calls), 2)


if __name__ == "__main__":
    unittest.main()
