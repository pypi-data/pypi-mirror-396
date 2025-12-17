# tests/test_environments_strict.py
import unittest

from anypoint_sdk._http import HttpClient
from anypoint_sdk.resources.environments import Environments
from tests.fakes import FakeSession
from tests.helpers import make_response

BASE = "https://api.test.local"


class _ListLogger:
    def __init__(self, name: str = "test"):
        self.name = name
        self.records: list[tuple[str, str]] = []

    def debug(self, msg, *a, **k):
        self.records.append(("DEBUG", (msg % a) if a else msg))

    def info(self, msg, *a, **k):
        self.records.append(("INFO", (msg % a) if a else msg))

    def warning(self, msg, *a, **k):
        self.records.append(("WARNING", (msg % a) if a else msg))

    def error(self, msg, *a, **k):
        self.records.append(("ERROR", (msg % a) if a else msg))

    def child(self, suffix: str):
        return self


class EnvironmentsStrictTests(unittest.TestCase):
    def test_raises_on_unauthorised_when_skip_is_false(self):
        # Arrange: a single unauthorised org
        orgs = [{"id": "o401"}]
        resp_401 = make_response(
            status=401,
            text="Unauthorized",
            url=f"{BASE}/accounts/api/organizations/o401/environments",
        )
        http = HttpClient(base_url=BASE, session=FakeSession([resp_401]), retries=0)
        envs_api = Environments(http)

        # Act / Assert: should raise because skip_unauthorised=False
        with self.assertRaises(Exception) as ctx:
            envs_api.list_by_orgs(orgs, skip_unauthorised=False)
        self.assertIn("HTTP 401", str(ctx.exception))

    def test_raises_on_non_skippable_status_even_when_skip_true(self):
        # Arrange: a server error, which is not in the skip set
        orgs = [{"id": "o500"}]
        resp_500 = make_response(
            status=500,
            text="Server Error",
            url=f"{BASE}/accounts/api/organizations/o500/environments",
        )
        http = HttpClient(base_url=BASE, session=FakeSession([resp_500]), retries=0)
        envs_api = Environments(http)

        # Act / Assert: skip_unauthorised=True, but 500 must still raise
        with self.assertRaises(Exception) as ctx:
            envs_api.list_by_orgs(orgs, skip_unauthorised=True)
        self.assertIn("HTTP 500", str(ctx.exception))

    def test_skips_on_401_when_skip_true(self):
        orgs = [{"id": "o401"}, {"id": "o2"}]
        r401 = make_response(
            status=401,
            text="Unauthorized",
            url=f"{BASE}/accounts/api/organizations/o401/environments",
        )
        ok = make_response(
            status=200,
            json_body={"data": [{"id": "e2", "name": "SB", "type": "sandbox"}]},
            url=f"{BASE}/accounts/api/organizations/o2/environments",
        )
        http = HttpClient(base_url=BASE, session=FakeSession([r401, ok]), retries=0)
        log = _ListLogger("scanner")
        envs = Environments(http, logger=log)
        out = envs.list_by_orgs(orgs, skip_unauthorised=True)
        self.assertEqual(set(out.keys()), {"o2"})
        self.assertTrue(
            any(
                level == "WARNING" and "No permission" in msg
                for level, msg in log.records
            )
        )

    def test_skips_on_403_when_skip_true(self):
        orgs = [{"id": "o403"}, {"id": "o2"}]
        r403 = make_response(
            status=403,
            text="Forbidden",
            url=f"{BASE}/accounts/api/organizations/o403/environments",
        )
        ok = make_response(
            status=200,
            json_body={"data": [{"id": "e2", "name": "SB", "type": "sandbox"}]},
            url=f"{BASE}/accounts/api/organizations/o2/environments",
        )
        http = HttpClient(base_url=BASE, session=FakeSession([r403, ok]), retries=0)
        log = _ListLogger("scanner")
        envs = Environments(http, logger=log)
        out = envs.list_by_orgs(orgs, skip_unauthorised=True)
        self.assertEqual(set(out.keys()), {"o2"})
        self.assertTrue(
            any(level == "WARNING" and "skipping" in msg for level, msg in log.records)
        )


if __name__ == "__main__":
    unittest.main()
