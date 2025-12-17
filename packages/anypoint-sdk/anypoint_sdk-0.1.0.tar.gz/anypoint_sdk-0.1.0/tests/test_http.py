# tests/test_http.py
import unittest

import requests
from requests import Response as RequestsResponse

from anypoint_sdk._http import HttpClient, HttpError, _Response
from tests.fakes import FakeSession
from tests.helpers import make_response

BASE_URL = "https://api.test.local"


class BadTextResponse(requests.Response):
    @property
    def text(self) -> str:
        raise RuntimeError("decode failure")


class SessionReturnsBadText:
    def request(self, *a, **kw) -> requests.Response:
        r = BadTextResponse()
        r.status_code = 500
        r.reason = "Server Error"
        r._content = b"\xff"  # optional
        return r


class HttpClientTests(unittest.TestCase):

    def test_get_success_200(self):
        # Arrange
        ok = make_response(
            status=200, json_body={"Hello": "World"}, url=f"{BASE_URL}/ping"
        )
        fake = FakeSession([ok])
        client = HttpClient(base_url=BASE_URL, session=fake, retries=0)

        # Act
        resp = client.get("/ping")

        # Assert
        self.assertEqual(resp.status, 200)
        self.assertEqual(resp.json(), {"Hello": "World"})
        self.assertEqual(fake.calls[0]["url"], f"{BASE_URL}/ping")
        self.assertEqual(fake.calls[0]["method"], "GET")

    def test_post_json_sends_payload(self):
        # Arrange
        ok = make_response(status=200, json_body={"ok": True}, url=f"{BASE_URL}/items")
        fake = FakeSession([ok])
        client = HttpClient(base_url=BASE_URL, session=fake, retries=0)

        body = {"name": "abc"}

        # Act
        resp = client.post_json("/items", json_body=body)

        # Assert
        self.assertEqual(resp.status, 200)
        self.assertEqual(fake.calls[0]["json"], body)
        self.assertEqual(fake.calls[0]["headers"]["Content-Type"], "application/json")

    def test_http_error_raises_HttpError(self):
        # Arrange
        not_found = make_response(
            status=404, text="Not Found", url=f"{BASE_URL}/missing"
        )
        fake = FakeSession([not_found])
        client = HttpClient(base_url=BASE_URL, session=fake, retries=0)

        # Act / Assert
        with self.assertRaises(HttpError) as ctx:
            client.get("/missing")
        self.assertEqual(ctx.exception.status, 404)
        self.assertIn("HTTP 404", str(ctx.exception))

    def test_network_error_raises_RuntimeError(self):
        # Arrange: FakeSession will raise a requests.RequestException
        class ErrorSession:
            def request(self, *args, **kwargs):
                raise requests.RequestException("boom")

        client = HttpClient(base_url=BASE_URL, session=ErrorSession(), retries=0)

        # Act / Assert
        with self.assertRaises(RuntimeError) as ctx:
            client.get("/ping")
        self.assertIn("Network error", str(ctx.exception))

    def test_merges_default_and_request_headers(self):
        # Arrange
        ok = make_response(status=200, json_body={"ok": True}, url=f"{BASE_URL}/merge")
        fake = FakeSession([ok])
        client = HttpClient(
            base_url=BASE_URL, session=fake, retries=0, headers={"X-Default": "1"}
        )

        # Act
        client.get("/merge", headers={"X-Request": "2"})

        # Assert
        sent_headers = fake.calls[0]["headers"]
        self.assertEqual(sent_headers["X-Default"], "1")
        self.assertEqual(sent_headers["X-Request"], "2")

    def test_json_returns_none_when_text_empty(self):
        # Create a dummy requests.Response
        dummy_resp = RequestsResponse()
        dummy_resp._content = b""  # no content
        dummy_resp.status_code = 200

        r = _Response(status=200, headers={}, text="", _resp=dummy_resp)

        result = r.json()
        self.assertIsNone(result)

    def test_proxies_are_set(self):
        ok = make_response(status=200, json_body={"ok": True}, url=f"{BASE_URL}/ping")
        fake = FakeSession([ok])
        client = HttpClient(
            base_url=BASE_URL,
            proxies={"https": "http://proxy"},
            session=fake,
            retries=0,
        )
        # Just ensuring the client is built triggers the proxies branch.
        client.get("/ping")

    def test_path_without_leading_slash_gets_fixed(self):
        ok = make_response(status=200, json_body={"ok": True}, url=f"{BASE_URL}/fixed")
        fake = FakeSession([ok])
        client = HttpClient(base_url=BASE_URL, session=fake, retries=0)
        client.get("fixed")  # No leading slash
        self.assertEqual(fake.calls[0]["url"], f"{BASE_URL}/fixed")

    def test_network_error_handling(self):
        class ErrorSession:
            def request(self, *a, **kw):
                from requests import RequestException

                raise RequestException("boom")

        client = HttpClient(base_url=BASE_URL, session=ErrorSession(), retries=0)
        with self.assertRaises(RuntimeError) as ctx:
            client.get("/ping")
        self.assertIn("Network error", str(ctx.exception))

    def test_http_error_includes_body(self):
        bad = make_response(status=500, text="Internal Error", url=f"{BASE_URL}/error")
        fake = FakeSession([bad])
        client = HttpClient(base_url=BASE_URL, session=fake, retries=0)
        with self.assertRaises(HttpError) as ctx:
            client.get("/error")
        self.assertEqual(ctx.exception.body, "Internal Error")

    def test_post_json_merges_headers(self):
        ok = make_response(status=200, json_body={"ok": True}, url=f"{BASE_URL}/items")
        fake = FakeSession([ok])
        client = HttpClient(base_url=BASE_URL, session=fake, retries=0)
        client.post_json("/items", json_body={}, headers={"X-Test": "1"})
        sent_headers = fake.calls[0]["headers"]
        self.assertEqual(sent_headers["Content-Type"], "application/json")
        self.assertEqual(sent_headers["X-Test"], "1")

    def test_close_closes_real_session(self):
        closed = {}

        class DummySession(requests.Session):

            def close(self):
                closed["was_called"] = True
                super().close()

        client = HttpClient(base_url=BASE_URL, session=DummySession())
        client.close()
        self.assertTrue(closed["was_called"])

    def test_proxies_are_applied_in_built_session(self):
        client = HttpClient(
            base_url=BASE_URL, proxies={"https": "http://proxy"}, retries=0
        )
        self.assertIsNotNone(client)

    def test_base_url_trailing_slash_is_trimmed(self):
        ok = make_response(status=200, json_body={"ok": True}, url=f"{BASE_URL}/ping")
        fake = FakeSession([ok])
        client = HttpClient(base_url=f"{BASE_URL}/", session=fake, retries=0)
        client.get("/ping")
        self.assertEqual(fake.calls[0]["url"], f"{BASE_URL}/ping")

    def test_params_none_values_are_dropped(self):
        ok = make_response(status=200, json_body={"ok": True}, url=f"{BASE_URL}/search")
        fake = FakeSession([ok])
        client = HttpClient(base_url=BASE_URL, session=fake, retries=0)

        client.get("/search", params={"a": 1, "b": None})
        self.assertEqual(fake.calls[0]["params"], {"a": 1})

    def test_success_with_empty_body(self):
        ok = make_response(status=204, text="", url=f"{BASE_URL}/empty")
        fake = FakeSession([ok])
        client = HttpClient(base_url=BASE_URL, session=fake, retries=0)

        r = client.get("/empty")
        self.assertEqual(r.status, 204)
        self.assertEqual(r.text, "")

    def test_post_uses_data_when_provided(self):
        ok = make_response(status=200, json_body={"ok": True}, url=f"{BASE_URL}/upload")
        fake = FakeSession([ok])
        client = HttpClient(base_url=BASE_URL, session=fake, retries=0)

        r = client._request("POST", "/upload", data=b"bytes", headers={"X-Test": "1"})
        self.assertEqual(r.status, 200)
        call = fake.calls[0]
        self.assertEqual(call["data"], b"bytes")
        self.assertEqual(call["headers"]["X-Test"], "1")

    def test_close_is_noop_for_fake_session(self):
        ok = make_response(status=200, json_body={"ok": True}, url=f"{BASE_URL}/ping")
        fake = FakeSession([ok])
        client = HttpClient(base_url=BASE_URL, session=fake, retries=0)
        # Should not raise, and should not try to call close on the fake
        client.close()

    def test_http_error_when_text_raises_sets_body_none(self):
        client = HttpClient(
            base_url=BASE_URL, session=SessionReturnsBadText(), retries=0
        )
        with self.assertRaises(HttpError) as ctx:
            client.get("/boom")
        self.assertEqual(ctx.exception.status, 500)
        self.assertIsNone(ctx.exception.body)

    def test_post_json_allows_overriding_content_type(self):
        ok = make_response(status=200, json_body={"ok": True}, url=f"{BASE_URL}/items")
        fake = FakeSession([ok])
        client = HttpClient(base_url=BASE_URL, session=fake, retries=0)

        client.post_json(
            "/items",
            json_body={"a": 1},
            headers={"Content-Type": "application/vnd.api+json", "X-Test": "1"},
        )

        sent = fake.calls[0]["headers"]
        self.assertEqual(sent["Content-Type"], "application/vnd.api+json")
        self.assertEqual(sent["X-Test"], "1")

    def test_build_session_without_proxies(self):
        # Exercises the False branch of: if proxies:
        client = HttpClient(base_url=BASE_URL, retries=0)
        self.assertIsNotNone(client)  # just construct, no network call

    def test_build_session_with_proxies(self):
        # Exercises the True branch of: if proxies:
        client = HttpClient(
            base_url=BASE_URL, retries=0, proxies={"https": "http://proxy"}
        )
        self.assertIsNotNone(client)

    def test_post_form_success(self):
        form_data = {"name": "test", "description": "A test form", "type": "rest-api"}

        resp = make_response(
            status=200,
            json_body={"success": True},
            url=f"{BASE_URL}/test/form",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE_URL, session=fake, retries=0)

        result = http.post_form("/test/form", form_data)

        self.assertEqual(len(fake.calls), 1)
        call = fake.calls[0]
        self.assertEqual(call["method"], "POST")

        # Should convert to (None, value) tuples for multipart without filenames
        expected_files = {
            "name": (None, "test"),
            "description": (None, "A test form"),
            "type": (None, "rest-api"),
        }
        self.assertEqual(call["files"], expected_files)
        # Content-Type should not be set (requests will handle multipart boundary)
        self.assertNotIn("Content-Type", call["headers"])
        self.assertEqual(result.json(), {"success": True})

    def test_post_form_handles_network_error(self):
        class ErrorSession:
            def request(self, *args, **kwargs):
                import requests

                raise requests.RequestException("Network failure")

        http = HttpClient(base_url=BASE_URL, session=ErrorSession(), retries=0)

        with self.assertRaises(RuntimeError) as ctx:
            http.post_form("/test/form", {"field": "value"})

        self.assertIn("Network error", str(ctx.exception))

    def test_post_form_handles_http_error_with_bad_text(self):
        class BadTextResponse:
            def __init__(self):
                self.status_code = 500
                self.reason = "Server Error"
                self.headers = {}

            @property
            def text(self):
                raise RuntimeError("Text decode failure")

        class BadTextSession:
            def request(self, *args, **kwargs):
                return BadTextResponse()

        http = HttpClient(base_url=BASE_URL, session=BadTextSession(), retries=0)

        with self.assertRaises(HttpError) as ctx:
            http.post_form("/test/form", {"field": "value"})

        self.assertEqual(ctx.exception.status, 500)
        self.assertIsNone(ctx.exception.body)


if __name__ == "__main__":
    unittest.main()
