# src/anypoint_sdk/resources/apis.py
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, Iterable, List, Optional

from .._http import HttpClient
from .._logging import LoggerLike, default_logger


@dataclass(frozen=True)
class ApiInstance:
    id: int
    groupId: str
    assetId: str
    assetVersion: Optional[str] = None
    productVersion: Optional[str] = None
    environmentId: Optional[str] = None
    instanceLabel: Optional[str] = None
    status: Optional[str] = None
    technology: Optional[str] = None
    activeContractsCount: Optional[int] = None
    exchangeAssetName: Optional[str] = None  # from enclosing asset object


def _to_instance(asset: Dict[str, Any], inst: Dict[str, Any]) -> ApiInstance:
    return ApiInstance(
        id=int(inst.get("id", 0)),
        groupId=str(inst.get("groupId", asset.get("groupId", ""))),
        assetId=str(inst.get("assetId", asset.get("assetId", ""))),
        assetVersion=(inst.get("assetVersion")),
        productVersion=(inst.get("productVersion")),
        environmentId=(inst.get("environmentId")),
        instanceLabel=(inst.get("instanceLabel")),
        status=(inst.get("status")),
        technology=(inst.get("technology")),
        activeContractsCount=inst.get("activeContractsCount"),
        exchangeAssetName=asset.get("exchangeAssetName"),
    )


def _dedupe(instances: Iterable[ApiInstance]) -> List[ApiInstance]:
    seen: set[int] = set()
    out: List[ApiInstance] = []
    for i in instances:
        if i.id and i.id not in seen:
            seen.add(i.id)
            out.append(i)
    return out


class APIs:
    """
    API Manager resources, minimal surface for listing and fetching instances.
    """

    def __init__(
        self, http: HttpClient, *, logger: Optional[LoggerLike] = None
    ) -> None:
        self._http = http
        self._log = logger or default_logger().child("resources.apis")

    def list_instances(
        self,
        org_id: str,
        env_id: str,
        *,
        offset: int = 0,
        limit: int = 200,
    ) -> List[Dict[str, Any]]:
        """
        List API instances in an environment.
        Returns a flattened list of dicts with keys like:
        id, groupId, assetId, assetVersion, productVersion, environmentId,
        instanceLabel, status, technology, activeContractsCount, exchangeAssetName.
        """
        r = self._http.get(
            f"/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/apis",
            params={"offset": offset, "limit": limit},
        )
        payload = r.json() or {}
        assets = payload.get("assets")
        if not isinstance(assets, list):
            assets = []

        instances: List[ApiInstance] = []
        for asset in assets:
            if not isinstance(asset, dict):
                continue
            for inst in asset.get("apis") or []:
                if isinstance(inst, dict):
                    instances.append(_to_instance(asset, inst))

        flat = [asdict(x) for x in _dedupe(instances)]
        self._log.debug(
            "Listed %d API instances for org=%s env=%s", len(flat), org_id, env_id
        )
        return flat

    def get_instance(
        self,
        org_id: str,
        env_id: str,
        api_id: int | str,
    ) -> Dict[str, Any]:
        """
        Fetch full details for a single API instance id.
        Returns the JSON object as provided by the API Manager detail endpoint.
        """
        r = self._http.get(
            f"/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/apis/{api_id}"
        )
        return r.json() or {}

    def create_instance(
        self,
        org_id: str,
        env_id: str,
        asset_id: str,
        asset_version: str,
        *,
        product_version: Optional[str] = None,
        instance_label: Optional[str] = None,
        upstream_url: Optional[str] = None,
        proxy_uri: Optional[str] = None,
        technology: str = "mule4",
        group_id: Optional[str] = None,
        promote: Optional[bool] = None,
        is_cloud_hub: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Create a new API instance in an environment."""
        payload: Dict[str, Any] = {
            "spec": {
                "assetId": asset_id,
                "version": asset_version,
            },
            "endpoint": {
                "type": "raml",
            },
            "technology": technology,
        }

        if product_version is not None:
            payload["productVersion"] = product_version
        if instance_label is not None:
            payload["instanceLabel"] = instance_label
        if upstream_url is not None:
            payload["endpoint"]["uri"] = upstream_url
        if proxy_uri is not None:
            payload["endpoint"]["proxyUri"] = proxy_uri
        if group_id is not None:
            payload["spec"]["groupId"] = group_id
        if promote is not None:
            payload["promote"] = promote
        if is_cloud_hub is not None:
            payload["endpoint"]["isCloudHub"] = is_cloud_hub

        r = self._http.post_json(
            f"/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/apis",
            json_body=payload,
        )

        result = r.json() or {}

        self._log.info(
            "Created API instance '%s' with id=%s in org=%s env=%s",
            asset_id,
            result.get("id"),
            org_id,
            env_id,
        )

        return result

    def update_instance(
        self,
        org_id: str,
        env_id: str,
        api_id: int | str,
        *,
        instance_label: Optional[str] = None,
        upstream_url: Optional[str] = None,
        proxy_uri: Optional[str] = None,
        is_cloud_hub: Optional[bool] = None,
        deployment_type: Optional[str] = None,
        response_timeout: Optional[int] = None,
        proxy_registration_uri: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Update an existing API instance.

        Args:
            org_id: The organization ID
            env_id: The environment ID
            api_id: The API instance ID to update
            instance_label: New label for the API instance
            upstream_url: Implementation URI (backend URL)
            proxy_uri: Consumer endpoint (proxy URL)
            is_cloud_hub: Whether deployed to CloudHub
            deployment_type: Deployment type (e.g., "CH", "HY", "RF")
            response_timeout: Response timeout in milliseconds
            proxy_registration_uri: Proxy registration URI

        Returns:
            Updated API instance details as a dict
        """
        payload: Dict[str, Any] = {}

        if instance_label is not None:
            payload["instanceLabel"] = instance_label

        # Endpoint-related updates go in the endpoint object
        endpoint: Dict[str, Any] = {}
        if upstream_url is not None:
            endpoint["uri"] = upstream_url
        if proxy_uri is not None:
            endpoint["proxyUri"] = proxy_uri
        if is_cloud_hub is not None:
            endpoint["isCloudHub"] = is_cloud_hub
        if deployment_type is not None:
            endpoint["deploymentType"] = deployment_type
        if response_timeout is not None:
            endpoint["responseTimeout"] = response_timeout
        if proxy_registration_uri is not None:
            endpoint["proxyRegistrationUri"] = proxy_registration_uri

        if endpoint:
            payload["endpoint"] = endpoint

        if not payload:
            # Nothing to update
            return self.get_instance(org_id, env_id, api_id)

        r = self._http._request(
            "PATCH",
            f"/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/apis/{api_id}",
            headers={"Content-Type": "application/json"},
            json_body=payload,
        )

        result = r.json() or {}

        self._log.info(
            "Updated API instance id=%s in org=%s env=%s",
            api_id,
            org_id,
            env_id,
        )

        return result

    def delete_instance(
        self,
        org_id: str,
        env_id: str,
        api_id: int | str,
    ) -> None:
        """Delete an API instance from an environment."""
        self._http._request(
            "DELETE",
            f"/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/apis/{api_id}",
        )
        self._log.info(
            "Deleted API instance id=%s from org=%s env=%s",
            api_id,
            org_id,
            env_id,
        )
