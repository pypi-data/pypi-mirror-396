# src/anypoint_sdk/_http.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Mapping, Optional, Protocol, Union

import requests
from requests import Response, Session
from requests.adapters import HTTPAdapter

try:
    from urllib3.util.retry import Retry
except Exception:  # pragma: no cover
    # Fallback for environments where urllib3 is vendored under requests
    from requests.packages.urllib3.util.retry import Retry  # type: ignore


class HttpError(Exception):
    def __init__(self, status: int, message: str, body: Optional[str] = None) -> None:
        super().__init__(f"HTTP {status}: {message}")
        self.status = status
        self.body = body


@dataclass
class _Response:
    status: int
    headers: Mapping[str, str]
    text: str
    _resp: Response

    def json(self) -> Any:
        if not self.text:
            return None
        return self._resp.json()


class HasRequest(Protocol):
    def request(self, method: str, url: str, *args: Any, **kwargs: Any) -> Response: ...


class HttpClient:
    """
    Small wrapper around requests.Session with base_url, default headers,
    timeouts, retries, and JSON helpers. Designed to be easy to unit test.
    """

    def __init__(
        self,
        base_url: str,
        headers: Optional[Mapping[str, str]] = None,
        timeout: float = 30.0,
        verify: Union[bool, str] = True,  # True or CA bundle path
        cert: Optional[Union[str, tuple[str, str]]] = None,  # client cert or (cert,key)
        proxies: Optional[Mapping[str, str]] = None,
        retries: int = 3,
        backoff_seconds: float = 0.5,
        session: Optional[HasRequest] = None,  # inject a fake in tests
    ) -> None:
        if base_url.endswith("/"):
            base_url = base_url[:-1]
        self._base_url = base_url
        self._default_headers = dict(headers or {})
        self._timeout = timeout
        self._verify = verify
        self._cert = cert

        self._session: HasRequest
        if session is not None:
            self._session = session
        else:
            self._session = self._build_session(
                retries=retries,
                backoff_seconds=backoff_seconds,
                proxies=proxies,
            )

    def _build_session(
        self,
        *,
        retries: int,
        backoff_seconds: float,
        proxies: Optional[Mapping[str, str]],
    ) -> Session:
        s = requests.Session()
        retry = Retry(
            total=retries,
            connect=retries,
            read=retries,
            status=retries,
            backoff_factor=backoff_seconds,
            status_forcelist=frozenset((429, 500, 502, 503, 504)),
            allowed_methods=frozenset(
                ("GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS")
            ),
            raise_on_status=False,
            respect_retry_after_header=True,
        )
        adapter = HTTPAdapter(max_retries=retry, pool_connections=10, pool_maxsize=50)
        s.mount("http://", adapter)
        s.mount("https://", adapter)
        if proxies:
            s.proxies.update(proxies)
        return s

    def _url(self, path: str) -> str:
        if not path.startswith("/"):
            path = "/" + path
        return self._base_url + path

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Mapping[str, Any]] = None,
        headers: Optional[Mapping[str, str]] = None,
        json_body: Any = None,
        data: Any = None,
    ) -> _Response:
        h = {**self._default_headers, **(headers or {})}
        try:
            resp = self._session.request(
                method=method.upper(),
                url=self._url(path),
                params={k: v for k, v in (params or {}).items() if v is not None},
                headers=h,
                timeout=self._timeout,
                verify=self._verify,
                cert=self._cert,
                json=json_body,
                data=data,
            )
        except requests.RequestException as e:
            raise RuntimeError(f"Network error: {e}") from None

        if 200 <= resp.status_code < 300:
            return _Response(
                status=resp.status_code,
                headers=dict(resp.headers),
                text=resp.text or "",
                _resp=resp,
            )

        body = None
        try:
            body = resp.text
        except Exception:
            body = None
        raise HttpError(resp.status_code, resp.reason or "Request failed", body)

    def get(
        self,
        path: str,
        params: Optional[Mapping[str, Any]] = None,
        headers: Optional[Mapping[str, str]] = None,
    ) -> _Response:
        return self._request("GET", path, params=params, headers=headers)

    def post_json(
        self,
        path: str,
        json_body: Any,
        params: Optional[Mapping[str, Any]] = None,
        headers: Optional[Mapping[str, str]] = None,
    ) -> _Response:
        h = {"Content-Type": "application/json", **(headers or {})}
        return self._request(
            "POST", path, params=params, headers=h, json_body=json_body
        )

    def close(self) -> None:
        if isinstance(self._session, Session):
            self._session.close()

    def post_form(
        self,
        path: str,
        form_data: Dict[str, Any],
        headers: Optional[Mapping[str, str]] = None,
    ) -> _Response:
        """Send a POST request with multipart form data."""
        h = {**self._default_headers, **(headers or {})}
        # Don't set Content-Type - requests will set it with boundary for multipart
        h.pop("Content-Type", None)

        # Convert form data to files format for multipart/form-data
        # Use (None, value) tuples to send as form fields without filenames
        files_data = {key: (None, value) for key, value in form_data.items()}

        try:
            resp = self._session.request(
                method="POST",
                url=self._url(path),
                params=None,
                headers=h,
                timeout=self._timeout,
                verify=self._verify,
                cert=self._cert,
                files=files_data,  # Use files parameter with (None, value) tuples
            )
        except requests.RequestException as e:
            raise RuntimeError(f"Network error: {e}") from None

        if 200 <= resp.status_code < 300:
            return _Response(
                status=resp.status_code,
                headers=dict(resp.headers),
                text=resp.text or "",
                _resp=resp,
            )

        body = None
        try:
            body = resp.text
        except Exception:
            body = None
        raise HttpError(resp.status_code, resp.reason or "Request failed", body)

    def post_form_ext(
        self,
        path: str,
        form_data: Dict[str, Any],
        headers: Optional[Mapping[str, str]] = None,
    ) -> _Response:
        """Send a POST request with multipart form data."""
        h = {**self._default_headers, **(headers or {})}
        # Don't set Content-Type - requests will handle multipart boundary
        h.pop("Content-Type", None)

        # Handle both simple values and file tuples
        files_data = {}
        for key, value in form_data.items():
            if isinstance(value, tuple) and len(value) >= 2:
                # File tuple: (filename, content, content_type)
                files_data[key] = value
            else:
                # Simple form field: convert to (None, value) tuple
                files_data[key] = (None, value)

        try:
            resp = self._session.request(
                method="POST",
                url=self._url(path),
                params=None,
                headers=h,
                timeout=self._timeout,
                verify=self._verify,
                cert=self._cert,
                files=files_data,
            )
        except requests.RequestException as e:
            raise RuntimeError(f"Network error: {e}") from None

        if 200 <= resp.status_code < 300:
            return _Response(
                status=resp.status_code,
                headers=dict(resp.headers),
                text=resp.text or "",
                _resp=resp,
            )

        body = None
        try:
            body = resp.text
        except Exception:
            body = None
        raise HttpError(resp.status_code, resp.reason or "Request failed", body)
