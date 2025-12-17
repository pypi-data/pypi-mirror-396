# src/anypoint_sdk/resources/applications.py
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, Iterable, List, Optional

from .._http import HttpClient
from .._logging import LoggerLike, default_logger


@dataclass(frozen=True)
class Application:
    id: int
    name: Optional[str] = None
    description: Optional[str] = None
    coreServicesId: Optional[str] = None
    url: Optional[str] = None

    # Credentials
    clientId: Optional[str] = None
    clientSecret: Optional[str] = None

    # Convenience owner fields
    ownerName: Optional[str] = None
    ownerEmail: Optional[str] = None

    # Collections
    grantTypes: Optional[List[str]] = None
    redirectUri: Optional[List[str]] = None
    owners: Optional[List[Dict[str, Any]]] = None

    # Timestamps as strings, unchanged
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None


def _norm_str_list(value: Any) -> Optional[List[str]]:
    if isinstance(value, list):
        out: List[str] = []
        for v in value:
            if isinstance(v, str):
                out.append(v)
        return out
    return None


def _norm_owners(value: Any) -> Optional[List[Dict[str, Any]]]:
    if not isinstance(value, list):
        return None
    out: List[Dict[str, Any]] = []
    for v in value:
        if isinstance(v, dict):
            # keep a small stable subset
            out.append(
                {
                    "id": v.get("id"),
                    "organizationId": v.get("organizationId"),
                    "firstName": v.get("firstName"),
                    "lastName": v.get("lastName"),
                    "email": v.get("email"),
                    "username": v.get("username"),
                    "entityType": v.get("entityType"),
                }
            )
    return out or None


def _to_application(obj: Dict[str, Any]) -> Application:
    audit = obj.get("audit") if isinstance(obj.get("audit"), dict) else None
    created = None
    updated = None
    if audit and isinstance(audit.get("created"), dict):
        created = audit["created"].get("date")
    if audit and isinstance(audit.get("updated"), dict):
        updated = audit["updated"].get("date")

    owner_name = obj.get("owner")
    owner_email = obj.get("email")
    owners = _norm_owners(obj.get("owners"))

    return Application(
        id=int(obj.get("id", 0)),
        name=obj.get("name"),
        description=obj.get("description"),
        coreServicesId=obj.get("coreServicesId"),
        url=obj.get("url"),
        clientId=obj.get("clientId"),
        clientSecret=obj.get("clientSecret"),
        ownerName=owner_name,
        ownerEmail=owner_email,
        grantTypes=_norm_str_list(obj.get("grantTypes")),
        redirectUri=_norm_str_list(obj.get("redirectUri")),
        owners=owners,
        createdAt=created,
        updatedAt=updated,
    )


def _dedupe(items: Iterable[Application]) -> List[Application]:
    seen: set[int] = set()
    out: List[Application] = []
    for it in items:
        if it.id and it.id not in seen:
            seen.add(it.id)
            out.append(it)
    return out


class Applications:
    """
    Connected client applications registered in the organisation.
    Data source: /apiplatform/repository/v2/organizations/{org_id}/applications?targetAdminSite=true
    """

    def __init__(
        self, http: HttpClient, *, logger: Optional[LoggerLike] = None
    ) -> None:
        self._http = http
        self._log = logger or default_logger().child("resources.applications")

    def list(
        self,
        org_id: str,
        *,
        target_admin_site: bool = True,
        offset: int = 0,
        limit: int = 200,
    ) -> List[Dict[str, Any]]:
        """
        List client applications for the given organisation.

        Returns a list of dicts with keys:
        id, name, description, coreServicesId, url, clientId, clientSecret,
        ownerName, ownerEmail, grantTypes, redirectUri, owners, createdAt, updatedAt.
        """
        params = {
            "targetAdminSite": "true" if target_admin_site else "false",
            "offset": offset,
            "limit": limit,
        }
        r = self._http.get(
            f"/apiplatform/repository/v2/organizations/{org_id}/applications",
            params=params,
        )
        payload = r.json() or {}
        raw = payload.get("applications")
        if not isinstance(raw, list):
            raw = []

        items: List[Application] = []
        for obj in raw:
            if isinstance(obj, dict):
                items.append(_to_application(obj))

        flat = [asdict(x) for x in _dedupe(items)]
        self._log.debug(
            "Listed %d applications for org=%s (targetAdminSite=%s)",
            len(flat),
            org_id,
            params["targetAdminSite"],
        )
        return flat

    def create(
        self,
        org_id: str,
        name: str,
        *,
        description: Optional[str] = None,
        url: Optional[str] = None,
        grant_types: Optional[List[str]] = None,
        redirect_uris: Optional[List[str]] = None,
        api_endpoints: bool = False,
    ) -> Dict[str, Any]:
        """
        Create a new client application in the organization.

        Args:
            org_id: Organization ID where the application will be created
            name: Application name (required)
            description: Optional description of the application
            url: Optional application URL
            grant_types: OAuth grant types (e.g., ["client_credentials", "authorization_code"])
            redirect_uris: OAuth redirect URIs for authorization flows
            api_endpoints: Whether to automatically register redirect URIs

        Returns:
            Dict containing the created application with keys:
            id, name, description, clientId, clientSecret, etc.

        Raises:
            HttpError: If the request fails (400, 401, 403, etc.)
            RuntimeError: If there's a network error
        """
        payload: Dict[str, Any] = {
            "name": name,
            "apiEndpoints": api_endpoints,
        }

        # Add optional fields
        if description is not None:
            payload["description"] = description
        if url is not None:
            payload["url"] = url
        if grant_types is not None:
            payload["grantTypes"] = grant_types
        if redirect_uris is not None:
            payload["redirectUri"] = redirect_uris

        r = self._http.post_json(
            f"/apiplatform/repository/v2/organizations/{org_id}/applications",
            json_body=payload,
        )

        result = r.json() or {}

        self._log.info(
            "Created application '%s' with id=%s in org=%s",
            name,
            result.get("id"),
            org_id,
        )

        return result

    def update(
        self,
        org_id: str,
        app_id: int | str,
        name: str,
        *,
        description: Optional[str] = None,
        url: Optional[str] = None,
        grant_types: Optional[List[str]] = None,
        redirect_uris: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Update an existing client application.

        Note: This uses PUT and requires at least the name field.

        Args:
            org_id: Organization ID containing the application
            app_id: Application ID to update
            name: Application name (required)
            description: Optional description of the application
            url: Optional application URL
            grant_types: OAuth grant types (e.g., ["client_credentials", "authorization_code"])
            redirect_uris: OAuth redirect URIs for authorization flows

        Returns:
            Dict containing the updated application details

        Raises:
            HttpError: If the request fails (400, 404, etc.)
        """
        payload: Dict[str, Any] = {"name": name}

        if description is not None:
            payload["description"] = description
        if url is not None:
            payload["url"] = url
        if grant_types is not None:
            payload["grantTypes"] = grant_types
        if redirect_uris is not None:
            payload["redirectUri"] = redirect_uris

        r = self._http._request(
            "PUT",
            f"/apiplatform/repository/v2/organizations/{org_id}/applications/{app_id}",
            headers={"Content-Type": "application/json"},
            json_body=payload,
        )
        result = r.json() or {}

        self._log.info(
            "Updated application '%s' (id=%s) in org=%s",
            name,
            app_id,
            org_id,
        )
        return result

    def delete(
        self,
        org_id: str,
        app_id: int | str,
    ) -> None:
        """Delete a client application from the organization."""
        self._http._request(
            "DELETE",
            f"/apiplatform/repository/v2/organizations/{org_id}/applications/{app_id}",
        )

        self._log.info(
            "Deleted application id=%s from org=%s",
            app_id,
            org_id,
        )
