# src/anypoint_sdk/resources/contracts.py
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, Iterable, List, Optional

from .._http import HttpClient
from .._logging import LoggerLike, default_logger


@dataclass(frozen=True)
class ApiContract:
    id: int
    status: Optional[str] = None
    approvedDate: Optional[str] = None
    rejectedDate: Optional[str] = None
    revokedDate: Optional[str] = None
    condition: Optional[str] = None

    apiId: Optional[int] = None

    applicationId: Optional[int] = None
    applicationName: Optional[str] = None

    tierId: Optional[int] = None
    tierName: Optional[str] = None
    tierLimits: Optional[List[Dict[str, Any]]] = None


def _to_api_contract(obj: Dict[str, Any]) -> ApiContract:
    # Nested optional sections
    app = obj.get("application") if isinstance(obj.get("application"), dict) else None
    tier = obj.get("tier") if isinstance(obj.get("tier"), dict) else None

    limits = None
    if tier and isinstance(tier.get("limits"), list):
        limits = [x for x in tier["limits"] if isinstance(x, dict)]

    return ApiContract(
        id=int(obj.get("id", 0)),
        status=obj.get("status"),
        approvedDate=obj.get("approvedDate"),
        rejectedDate=obj.get("rejectedDate"),
        revokedDate=obj.get("revokedDate"),
        condition=obj.get("condition"),
        apiId=(obj.get("apiId")),
        applicationId=(app.get("id") if app else None),
        applicationName=(app.get("name") if app else None),
        tierId=(tier.get("id") if tier else None),
        tierName=(tier.get("name") if tier else None),
        tierLimits=limits,
    )


def _dedupe(items: Iterable[ApiContract]) -> List[ApiContract]:
    seen: set[int] = set()
    out: List[ApiContract] = []
    for it in items:
        if it.id and it.id not in seen:
            seen.add(it.id)
            out.append(it)
    return out


class Contracts:
    """
    API Manager contracts, minimal surface for API instance contracts.
    """

    def __init__(
        self, http: HttpClient, *, logger: Optional[LoggerLike] = None
    ) -> None:
        self._http = http
        self._log = logger or default_logger().child("resources.contracts")

    def list_api_contracts(
        self,
        org_id: str,
        env_id: str,
        api_id: int | str,
        *,
        offset: int = 0,
        limit: int = 200,
    ) -> List[Dict[str, Any]]:
        """
        List client contracts for an API instance.

        Returns a list of dicts with keys like:
        id, status, approvedDate, rejectedDate, revokedDate, condition,
        apiId, applicationId, applicationName, tierId, tierName, tierLimits.
        """
        r = self._http.get(
            f"/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/apis/{api_id}/contracts",
            params={"offset": offset, "limit": limit},
        )
        payload = r.json() or {}
        raw = payload.get("contracts")
        if not isinstance(raw, list):
            raw = []

        items: List[ApiContract] = []
        for obj in raw:
            if isinstance(obj, dict):
                items.append(_to_api_contract(obj))

        flat = [asdict(x) for x in _dedupe(items)]
        self._log.debug(
            "Listed %d API contracts for org=%s env=%s api=%s",
            len(flat),
            org_id,
            env_id,
            api_id,
        )
        return flat

    def list_group_contracts(
        self,
        org_id: str,
        env_id: str,
        group_id: int | str,
        *,
        offset: int = 0,
        limit: int = 200,
    ) -> List[Dict[str, Any]]:
        """
        List client contracts for a group instance.

        Returns a list of dicts similar to API contracts, with additional tier fields:
        tierDefaultLimits, tierLimitsByApi. Shapes are normalised and deduped by id.
        """
        r = self._http.get(
            f"/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/groupInstances/{group_id}/contracts",
            params={"offset": offset, "limit": limit},
        )
        payload = r.json() or {}
        raw = payload.get("contracts")
        if not isinstance(raw, list):
            raw = []

        items: List[ApiContract] = []
        out: List[Dict[str, Any]] = []
        for obj in raw:
            if not isinstance(obj, dict):
                continue
            # Reuse ApiContract normalisation for shared fields
            base = _to_api_contract(obj)
            items.append(base)

            # Add group specific fields from tier, if present
            tier = obj.get("tier") if isinstance(obj.get("tier"), dict) else None
            default_limits = None
            limits_by_api = None
            if tier:
                if isinstance(tier.get("defaultLimits"), list):
                    default_limits = [
                        x for x in tier["defaultLimits"] if isinstance(x, dict)
                    ]
                if isinstance(tier.get("limitsByApi"), list):
                    limits_by_api = [
                        x for x in tier["limitsByApi"] if isinstance(x, dict)
                    ]

            row = asdict(base)
            row["tierDefaultLimits"] = default_limits
            row["tierLimitsByApi"] = limits_by_api
            out.append(row)

        # Deduplicate by id
        seen: set[int] = set()
        deduped: List[Dict[str, Any]] = []
        for row in out:
            cid = int(row.get("id", 0))
            if cid and cid not in seen:
                seen.add(cid)
                deduped.append(row)

        self._log.debug(
            "Listed %d group contracts for org=%s env=%s group=%s",
            len(deduped),
            org_id,
            env_id,
            group_id,
        )
        return deduped

    def create_contract(
        self,
        org_id: str,
        env_id: str,
        api_id: int | str,
        application_id: int | str,
        *,
        tier_id: Optional[int | str] = None,
    ) -> Dict[str, Any]:
        """
        Create a contract between a client application and an API instance.

        Args:
            org_id: The organization ID
            env_id: The environment ID
            api_id: The API instance ID
            application_id: The client application ID
            tier_id: Optional SLA tier ID for the contract

        Returns:
            Created contract details as a dict with keys like:
            id, status, applicationId, apiId, tierId, etc.

        Raises:
            HttpError: If the request fails (400, 404, etc.)
        """
        payload: Dict[str, Any] = {"applicationId": int(application_id)}
        if tier_id is not None:
            payload["tierId"] = int(tier_id)

        r = self._http.post_json(
            f"/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/apis/{api_id}/contracts",
            json_body=payload,
        )
        result = r.json() or {}

        self._log.info(
            "Created contract id=%s for app=%s on api=%s in org=%s env=%s",
            result.get("id"),
            application_id,
            api_id,
            org_id,
            env_id,
        )
        return result

    def revoke_contract(
        self,
        org_id: str,
        env_id: str,
        api_id: int | str,
        contract_id: int | str,
    ) -> Dict[str, Any]:
        """
        Revoke an active contract. Contracts must be revoked before deletion.

        Args:
            org_id: The organization ID
            env_id: The environment ID
            api_id: The API instance ID
            contract_id: The contract ID to revoke

        Returns:
            Updated contract details as a dict

        Raises:
            HttpError: If the request fails (400, 404, etc.)
        """
        r = self._http._request(
            "PATCH",
            f"/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/apis/{api_id}/contracts/{contract_id}",
            headers={"Content-Type": "application/json"},
            json_body={"status": "REVOKED"},
        )
        result = r.json() or {}

        self._log.info(
            "Revoked contract id=%s for api=%s in org=%s env=%s",
            contract_id,
            api_id,
            org_id,
            env_id,
        )
        return result

    def delete_contract(
        self,
        org_id: str,
        env_id: str,
        api_id: int | str,
        contract_id: int | str,
    ) -> None:
        """
        Delete a revoked contract.

        Note: Contracts must be revoked before they can be deleted.
        Use revoke_contract() first if the contract is still active.

        Args:
            org_id: The organization ID
            env_id: The environment ID
            api_id: The API instance ID
            contract_id: The contract ID to delete

        Raises:
            HttpError: If the request fails (400 if contract is still active, 404, etc.)
        """
        self._http._request(
            "DELETE",
            f"/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/apis/{api_id}/contracts/{contract_id}",
        )

        self._log.info(
            "Deleted contract id=%s for api=%s in org=%s env=%s",
            contract_id,
            api_id,
            org_id,
            env_id,
        )
