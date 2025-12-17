# src/anypoint_sdk/resources/organizations.py
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, Iterable, List, Optional

from .._http import HttpClient
from .._logging import LoggerLike, default_logger


@dataclass(frozen=True)
class OrgSummary:
    id: str
    name: str
    parentId: Optional[str] = None
    isRoot: Optional[bool] = None
    isMaster: Optional[bool] = None


def _to_org_summary(obj: Dict[str, Any]) -> OrgSummary:
    parent_id: Optional[str] = obj.get("parentId")
    if parent_id is None:
        parents = obj.get("parentOrganizationIds")
        if isinstance(parents, list) and parents:
            parent_id = parents[0]
    return OrgSummary(
        id=str(obj.get("id", "")),
        name=str(obj.get("name", "")),
        parentId=parent_id,
        isRoot=obj.get("isRoot"),
        isMaster=obj.get("isMaster"),
    )


def _dedupe(orgs: Iterable[OrgSummary]) -> List[OrgSummary]:
    seen: set[str] = set()
    out: List[OrgSummary] = []
    for o in orgs:
        if o.id and o.id not in seen:
            seen.add(o.id)
            out.append(o)
    return out


class Organizations:
    def __init__(
        self, http: HttpClient, *, logger: Optional[LoggerLike] = None
    ) -> None:
        self._http = http
        self._log = logger or default_logger().child("resources.organizations")

    def me(self) -> Dict[str, Any]:
        r = self._http.get("/accounts/api/me")
        return r.json() or {}

    def list_accessible(self) -> List[Dict[str, Any]]:
        data = self.me()
        user = data.get("user") or {}

        collected: List[OrgSummary] = []

        primary_org = user.get("organization")
        if isinstance(primary_org, dict):
            collected.append(_to_org_summary(primary_org))

        members = (user.get("memberOfOrganizations") or []) + (
            data.get("memberOfOrganizations") or []
        )
        contributors = (user.get("contributorOfOrganizations") or []) + (
            data.get("contributorOfOrganizations") or []
        )

        for obj in members:
            if isinstance(obj, dict):
                collected.append(_to_org_summary(obj))
        for obj in contributors:
            if isinstance(obj, dict):
                collected.append(_to_org_summary(obj))

        return [asdict(x) for x in _dedupe(collected)]
