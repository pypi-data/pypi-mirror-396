# src/anypoint_sdk/resources/environments.py
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, Iterable, List, Optional

from .._http import HttpClient, HttpError
from .._logging import LoggerLike, default_logger


@dataclass(frozen=True)
class EnvSummary:
    id: str
    name: str
    type: Optional[str] = None
    region: Optional[str] = None


def _to_env_summary(obj: Dict[str, Any]) -> EnvSummary:
    # MuleSoft responses usually include id, name, and type.
    # so being defensive about keys that may vary.
    env_type = obj.get("type") or obj.get("environmentType")
    region = obj.get("region") or obj.get("dataRegion")
    return EnvSummary(
        id=str(obj.get("id", "")),
        name=str(obj.get("name", "")),
        type=str(env_type) if env_type is not None else None,
        region=str(region) if region is not None else None,
    )


def _dedupe(envs: Iterable[EnvSummary]) -> List[EnvSummary]:
    seen: set[str] = set()
    out: List[EnvSummary] = []
    for e in envs:
        if e.id and e.id not in seen:
            seen.add(e.id)
            out.append(e)
    return out


class Environments:
    """
    Fetch and normalise environments for organisations.
    Caches results per organisation id for the lifetime of this instance.
    """

    def __init__(
        self, http: HttpClient, *, logger: Optional[LoggerLike] = None
    ) -> None:
        self._http = http
        self._cache: dict[str, List[EnvSummary]] = {}
        self._log = logger or default_logger().child("resources.environments")

    def list(self, org_id: str, *, use_cache: bool = True) -> List[Dict[str, Any]]:
        if use_cache and org_id in self._cache:
            return [asdict(x) for x in self._cache[org_id]]
        r = self._http.get(f"/accounts/api/organizations/{org_id}/environments")
        data = r.json() or []
        items = (data.get("data") or []) if isinstance(data, dict) else (data or [])
        envs = _dedupe(_to_env_summary(obj) for obj in items if isinstance(obj, dict))
        self._cache[org_id] = envs
        return [asdict(x) for x in envs]

    def list_by_orgs(
        self,
        orgs: List[Dict[str, Any]],
        *,
        use_cache: bool = True,
        skip_unauthorised: bool = True,
    ) -> Dict[str, List[Dict[str, Any]]]:
        out: dict[str, List[Dict[str, Any]]] = {}
        for org in orgs:
            org_id = str(org.get("id", ""))
            if not org_id:
                continue
            try:
                out[org_id] = self.list(org_id, use_cache=use_cache)
            except HttpError as e:
                if skip_unauthorised and e.status in (401, 403):
                    self._log.warning(
                        "No permission to list environments for organisation %s, HTTP %s, skipping.",
                        org_id,
                        e.status,
                    )
                    continue
                elif skip_unauthorised and e.status == 404:
                    self._log.warning(
                        "No Environments found for organisation %s, HTTP %s, skipping.",
                        org_id,
                        e.status,
                    )
                    continue
                raise
        return out

    def clear_cache(self) -> None:
        self._cache.clear()
