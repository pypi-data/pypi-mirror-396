# src/anypoint_sdk/resources/tiers.py
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, Iterable, List, Optional

from .._http import HttpClient
from .._logging import LoggerLike, default_logger


@dataclass(frozen=True)
class ApiTier:
    id: int
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    autoApprove: Optional[bool] = None
    applicationCount: Optional[int] = None
    limits: Optional[List[Dict[str, Any]]] = None  # list of dicts


def _to_api_tier(obj: Dict[str, Any]) -> ApiTier:
    raw_limits = obj.get("limits")
    limits = None
    if isinstance(raw_limits, list):
        limits = [x for x in raw_limits if isinstance(x, dict)]
    return ApiTier(
        id=int(obj.get("id", 0)),
        name=obj.get("name"),
        description=obj.get("description"),
        status=obj.get("status"),
        autoApprove=obj.get("autoApprove"),
        applicationCount=obj.get("applicationCount"),
        limits=limits,
    )


def _dedupe(items: Iterable[ApiTier]) -> List[ApiTier]:
    seen: set[int] = set()
    out: List[ApiTier] = []
    for it in items:
        if it.id and it.id not in seen:
            seen.add(it.id)
            out.append(it)
    return out


class Tiers:
    """
    API Manager tiers, minimal surface for API instance tiers.
    """

    def __init__(
        self, http: HttpClient, *, logger: Optional[LoggerLike] = None
    ) -> None:
        self._http = http
        self._log = logger or default_logger().child("resources.tiers")

    def list_api_tiers(
        self,
        org_id: str,
        env_id: str,
        api_id: int | str,
        *,
        offset: int = 0,
        limit: int = 200,
    ) -> List[Dict[str, Any]]:
        """
        List SLA tiers for an API instance.

        Returns a list of dicts with keys like:
        id, name, description, status, autoApprove, applicationCount, limits.
        """
        r = self._http.get(
            f"/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/apis/{api_id}/tiers",
            params={"offset": offset, "limit": limit},
        )
        payload = r.json() or {}
        raw = payload.get("tiers")
        if not isinstance(raw, List):
            # some endpoints use 'values'
            raw = payload.get("values")
        if not isinstance(raw, list):
            raw = []

        items: List[ApiTier] = []
        for obj in raw:
            if isinstance(obj, dict):
                items.append(_to_api_tier(obj))

        flat = [asdict(x) for x in _dedupe(items)]
        self._log.debug(
            "Listed %d API tiers for org=%s env=%s api=%s",
            len(flat),
            org_id,
            env_id,
            api_id,
        )
        return flat

    def list_group_tiers(
        self,
        org_id: str,
        env_id: str,
        group_id: int | str,
        *,
        offset: int = 0,
        limit: int = 200,
    ) -> List[Dict[str, Any]]:
        """
        List SLA tiers for a group instance.

        Returns normalised dicts with keys:
        id, name, description, status, autoApprove, applicationCount,
        defaultLimits, limitsByApi.
        """
        r = self._http.get(
            f"/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/groupInstances/{group_id}/tiers",
            params={"offset": offset, "limit": limit},
        )
        payload = r.json() or {}
        raw = payload.get("tiers")
        if not isinstance(raw, list):
            raw = payload.get("values")
        if not isinstance(raw, list):
            raw = []

        items: List[ApiTier] = []
        rows: List[Dict[str, Any]] = []
        for obj in raw:
            if not isinstance(obj, dict):
                continue
            tier = _to_api_tier(obj)

            # Group specific extras
            default_limits = None
            limits_by_api = None
            if isinstance(obj.get("defaultLimits"), list):
                default_limits = [
                    x for x in obj["defaultLimits"] if isinstance(x, dict)
                ]
            if isinstance(obj.get("limitsByApi"), list):
                limits_by_api = [x for x in obj["limitsByApi"] if isinstance(x, dict)]

            row = asdict(tier)
            row["defaultLimits"] = default_limits
            row["limitsByApi"] = limits_by_api
            items.append(tier)
            rows.append(row)

        # Deduplicate by id
        seen: set[int] = set()
        deduped: List[Dict[str, Any]] = []
        for row in rows:
            tid = int(row.get("id", 0))
            if tid and tid not in seen:
                seen.add(tid)
                deduped.append(row)

        self._log.debug(
            "Listed %d group tiers for org=%s env=%s group=%s",
            len(deduped),
            org_id,
            env_id,
            group_id,
        )
        return deduped

    def create_tier(
        self,
        org_id: str,
        env_id: str,
        api_id: int | str,
        name: str,
        limits: List[Dict[str, Any]],
        *,
        description: Optional[str] = None,
        auto_approve: bool = False,
        status: str = "ACTIVE",
    ) -> Dict[str, Any]:
        """
        Create an SLA tier for an API instance.

        Args:
            org_id: The organization ID
            env_id: The environment ID
            api_id: The API instance ID
            name: Name of the tier (e.g., "gold", "silver", "bronze")
            limits: List of rate limit configurations, each with keys like:
                    maximumRequests, timePeriodInMilliseconds
            description: Optional description of the tier
            auto_approve: Whether contract requests are auto-approved (default False)
            status: Tier status, typically "ACTIVE" or "INACTIVE" (default "ACTIVE")

        Returns:
            Created tier details as a dict with keys like:
            id, name, description, status, autoApprove, limits, apiId, etc.

        Raises:
            HttpError: If the request fails (400, 404, etc.)
        """
        payload: Dict[str, Any] = {
            "name": name,
            "status": status,
            "autoApprove": auto_approve,
            "limits": limits,
        }
        if description is not None:
            payload["description"] = description

        r = self._http.post_json(
            f"/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/apis/{api_id}/tiers",
            json_body=payload,
        )
        result = r.json() or {}

        self._log.info(
            "Created tier '%s' (id=%s) for api=%s in org=%s env=%s",
            name,
            result.get("id"),
            api_id,
            org_id,
            env_id,
        )
        return result

    def update_tier(
        self,
        org_id: str,
        env_id: str,
        api_id: int | str,
        tier_id: int | str,
        name: str,
        limits: List[Dict[str, Any]],
        *,
        description: Optional[str] = None,
        auto_approve: bool = False,
        status: str = "ACTIVE",
    ) -> Dict[str, Any]:
        """
        Update an SLA tier for an API instance.

        Note: This uses PUT and requires the full tier definition.

        Args:
            org_id: The organization ID
            env_id: The environment ID
            api_id: The API instance ID
            tier_id: The tier ID to update
            name: Name of the tier
            limits: List of rate limit configurations
            description: Optional description of the tier
            auto_approve: Whether contract requests are auto-approved
            status: Tier status, typically "ACTIVE" or "INACTIVE"

        Returns:
            Updated tier details as a dict

        Raises:
            HttpError: If the request fails (400, 404, etc.)
        """
        payload: Dict[str, Any] = {
            "name": name,
            "status": status,
            "autoApprove": auto_approve,
            "limits": limits,
        }
        if description is not None:
            payload["description"] = description

        r = self._http._request(
            "PUT",
            f"/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/apis/{api_id}/tiers/{tier_id}",
            headers={"Content-Type": "application/json"},
            json_body=payload,
        )
        result = r.json() or {}

        self._log.info(
            "Updated tier '%s' (id=%s) for api=%s in org=%s env=%s",
            name,
            tier_id,
            api_id,
            org_id,
            env_id,
        )
        return result

    def delete_tier(
        self,
        org_id: str,
        env_id: str,
        api_id: int | str,
        tier_id: int | str,
    ) -> None:
        """
        Delete an SLA tier from an API instance.

        Args:
            org_id: The organization ID
            env_id: The environment ID
            api_id: The API instance ID
            tier_id: The tier ID to delete

        Raises:
            HttpError: If the request fails (400, 404, etc.)
        """
        self._http._request(
            "DELETE",
            f"/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/apis/{api_id}/tiers/{tier_id}",
        )

        self._log.info(
            "Deleted tier id=%s for api=%s in org=%s env=%s",
            tier_id,
            api_id,
            org_id,
            env_id,
        )
