# src/anypoint_sdk/resources/groups.py
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, Iterable, List, Optional, Set

from .._http import HttpClient
from .._logging import LoggerLike, default_logger


@dataclass(frozen=True)
class GroupInstance:
    id: int
    groupName: Optional[str] = None
    groupVersionName: Optional[str] = None
    status: Optional[str] = None
    deprecated: Optional[bool] = None
    environmentId: Optional[str] = None
    apiInstanceIds: Optional[List[int]] = None  # ids of API instances in this group


def _extract_api_ids(obj: Dict[str, Any]) -> List[int]:
    """
    apiInstances can be a list of dicts with 'id', or a list of raw ints.
    Be forgiving and filter out bad shapes.
    """
    raw = obj.get("apiInstances")
    if not isinstance(raw, list):
        return []
    out: List[int] = []
    for it in raw:
        if isinstance(it, dict) and "id" in it:
            try:
                out.append(int(it["id"]))
            except Exception:
                continue
        elif isinstance(it, int):
            out.append(it)
    return out


def _to_group_instance(obj: Dict[str, Any]) -> GroupInstance:
    return GroupInstance(
        id=int(obj.get("id", 0)),
        groupName=obj.get("groupName"),
        groupVersionName=obj.get("groupVersionName"),
        status=obj.get("status"),
        deprecated=obj.get("deprecated"),
        environmentId=obj.get("environmentId"),
        apiInstanceIds=_extract_api_ids(obj),
    )


def _dedupe(groups: Iterable[GroupInstance]) -> List[GroupInstance]:
    seen: Set[int] = set()
    out: List[GroupInstance] = []
    for g in groups:
        if g.id and g.id not in seen:
            seen.add(g.id)
            out.append(g)
    return out


class GroupInstances:
    """
    API Manager group instances in an environment.
    """

    def __init__(
        self, http: HttpClient, *, logger: Optional[LoggerLike] = None
    ) -> None:
        self._http = http
        self._log = logger or default_logger().child("resources.groups")

    def list(
        self,
        org_id: str,
        env_id: str,
        *,
        offset: int = 0,
        limit: int = 200,
    ) -> List[Dict[str, Any]]:
        """
        List group instances for an environment.
        Returns normalised dicts with keys:
        id, groupName, groupVersionName, status, deprecated, environmentId, apiInstanceIds.
        """
        r = self._http.get(
            f"/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/groupInstances",
            params={"offset": offset, "limit": limit},
        )
        payload = r.json() or {}
        raw = payload.get("instances")
        if not isinstance(raw, list):
            raw = []

        items: List[GroupInstance] = []
        for obj in raw:
            if isinstance(obj, dict):
                items.append(_to_group_instance(obj))

        flat = [asdict(x) for x in _dedupe(items)]
        self._log.debug(
            "Listed %d group instances for org=%s env=%s",
            len(flat),
            org_id,
            env_id,
        )
        return flat

    def get(
        self, org_id: str, env_id: str, group_instance_id: int | str
    ) -> Dict[str, Any]:
        """
        Return the raw detail JSON for a group instance.
        """
        r = self._http.get(
            f"/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/groupInstances/{group_instance_id}"
        )
        return r.json() or {}

    def find_group_for_api(
        self,
        org_id: str,
        env_id: str,
        api_id: int | str,
    ) -> Optional[int]:
        """
        Try to locate the group instance id that contains the given API instance id.

        Strategy:
        1) Use the 'apiInstances' list from list() if present.
        2) If not conclusive, fetch each group's detail and check its 'apiInstances'.
        Returns the first matching group id, or None if not found.
        """
        api_id_int = int(api_id)
        groups = self.list(org_id, env_id)

        # First pass, try to match from the list payload itself.
        for g in groups:
            ids = g.get("apiInstanceIds") or []
            if api_id_int in ids:
                self._log.debug(
                    "Matched API %s to group %s using list payload.",
                    api_id_int,
                    g["id"],
                )
                return int(g["id"])

        # Second pass, fetch details if the list did not include apiInstances or was inconclusive.
        for g in groups:
            gid = g.get("id")
            if not gid:
                continue
            detail = self.get(org_id, env_id, gid)
            ids = _extract_api_ids(detail)
            if api_id_int in ids:
                self._log.debug(
                    "Matched API %s to group %s using detail fetch.", api_id_int, gid
                )
                return int(gid)

        return None
