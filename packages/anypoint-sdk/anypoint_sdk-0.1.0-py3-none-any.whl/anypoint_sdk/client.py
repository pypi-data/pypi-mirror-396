# src/anypoint_sdk/client.py
from __future__ import annotations

from typing import Optional

from ._http import HttpClient
from ._logging import LoggerLike, default_logger
from ._version import __version__ as SDK_VERSION
from .auth import TokenAuth, get_token_with_client_credentials
from .resources.apis import APIs
from .resources.applications import Applications
from .resources.contracts import Contracts
from .resources.environments import Environments
from .resources.exchange import Exchange
from .resources.groups import GroupInstances
from .resources.observability import Observability
from .resources.organizations import Organizations
from .resources.policies import Policies
from .resources.tiers import Tiers

DEFAULT_BASE_URL = "https://anypoint.mulesoft.com"
DEFAULT_USER_AGENT = f"anypoint-sdk/{SDK_VERSION}"


class AnypointClient:
    """
    SDK entry point. Consturct with an already aquired token, or use
    from_client_credentials to exchange a client id and a secret for a token
    """

    def __init__(
        self,
        token: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 30.0,
        verify: bool | str = True,
        cert: Optional[str | tuple[str, str]] = None,
        extra_headers: Optional[dict[str, str]] = None,
        proxies: Optional[dict[str, str]] = None,
        logger: Optional[LoggerLike] = None,
    ) -> None:
        self._log: LoggerLike = logger or default_logger()
        auth = TokenAuth(token=token)
        headers = {
            "User-Agent": DEFAULT_USER_AGENT,
            **auth.as_header(),
            **(extra_headers or {}),
        }
        self._http = HttpClient(
            base_url=base_url,
            headers=headers,
            timeout=timeout,
            verify=verify,
            cert=cert,
            proxies=proxies,
        )
        self.organizations = Organizations(
            self._http, logger=self._log.child("resources.organizations")
        )
        self.environments = Environments(
            self._http, logger=self._log.child("resources.environments")
        )
        self.apis = APIs(self._http, logger=self._log.child("resources.apis"))
        self.policies = Policies(
            self._http, logger=self._log.child("resources.policies")
        )
        self.contracts = Contracts(
            self._http, logger=self._log.child("resources.contracts")
        )
        self.tiers = Tiers(self._http, logger=self._log.child("resources.tiers"))
        self.groups = GroupInstances(
            self._http, logger=self._log.child("resources.groups")
        )
        self.applications = Applications(
            self._http, logger=self._log.child("resources.applications")
        )
        self.exchange = Exchange(
            self._http, logger=self._log.child("resources.exchange")
        )
        self.observability = Observability(
            self._http, logger=self._log.child("resources.observability")
        )

    @classmethod
    def from_client_credentials(
        cls, client_id: str, client_secret: str, **kwargs
    ) -> "AnypointClient":
        base_url = kwargs.get("base_url", DEFAULT_BASE_URL)
        timeout = kwargs.get("timeout", 30.0)
        verify = kwargs.get("verify", True)
        cert = kwargs.get("cert", None)
        proxies = kwargs.get("proxies", None)
        extra_headers = kwargs.get("extra_headers", None)
        logger: Optional[LoggerLike] = kwargs.get("logger", None)

        bootstrap = HttpClient(
            base_url=base_url,
            headers={"User-Agent": DEFAULT_USER_AGENT, **(extra_headers or {})},
            timeout=timeout,
            verify=verify,
            cert=cert,
            proxies=proxies,
        )
        try:
            token = get_token_with_client_credentials(
                bootstrap, client_id=client_id, client_secret=client_secret
            ).access_token
        finally:
            bootstrap.close()

        return cls(
            token=token,
            base_url=base_url,
            timeout=timeout,
            verify=verify,
            cert=cert,
            extra_headers=extra_headers,
            proxies=proxies,
            logger=logger,
        )

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> "AnypointClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def get_token(self) -> str:
        """Return the bearer token for debugging purposes."""
        auth_header = self._http._default_headers.get("Authorization", "")
        return auth_header.replace("Bearer ", "")
