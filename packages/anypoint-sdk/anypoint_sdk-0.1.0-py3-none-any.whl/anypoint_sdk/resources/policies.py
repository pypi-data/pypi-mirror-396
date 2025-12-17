# src/anypoint_sdk/resources/policies.py
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, Iterable, List, Optional

from .._http import HttpClient
from .._logging import LoggerLike, default_logger


@dataclass(frozen=True)
class ApiPolicy:
    policyId: int
    policyTemplateId: Optional[str] = None
    type: Optional[str] = None  # "system" or "custom"
    order: Optional[int] = None
    implementationAsset: Optional[Dict[str, Any]] = None
    configuration: Optional[Dict[str, Any]] = None


def _to_api_policy(obj: Dict[str, Any]) -> ApiPolicy:
    return ApiPolicy(
        policyId=int(obj.get("policyId", 0)),
        policyTemplateId=obj.get("policyTemplateId"),
        type=obj.get("type"),
        order=obj.get("order"),
        implementationAsset=obj.get("implementationAsset"),
        configuration=obj.get("configuration"),
    )


def _dedupe(policies: Iterable[ApiPolicy]) -> List[ApiPolicy]:
    seen: set[int] = set()
    out: List[ApiPolicy] = []
    for p in policies:
        if p.policyId and p.policyId not in seen:
            seen.add(p.policyId)
            out.append(p)
    return out


@dataclass(frozen=True)
class AutomatedPolicy:
    id: int
    assetId: Optional[str] = None
    assetVersion: Optional[str] = None
    order: Optional[int] = None
    disabled: Optional[bool] = None
    configurationData: Optional[Dict[str, Any]] = None
    implementationAssets: Optional[List[Dict[str, Any]]] = None  # list of dicts


def _to_automated_policy(obj: Dict[str, Any]) -> AutomatedPolicy:
    impl_assets = obj.get("implementationAssets")
    if not isinstance(impl_assets, list):
        impl_assets = []
    cfg = obj.get("configurationData")
    if not isinstance(cfg, dict):
        cfg = None
    return AutomatedPolicy(
        id=int(obj.get("id", 0)),
        assetId=obj.get("assetId"),
        assetVersion=obj.get("assetVersion"),
        order=obj.get("order"),
        disabled=obj.get("disabled"),
        configurationData=cfg,
        implementationAssets=[ia for ia in impl_assets if isinstance(ia, dict)],
    )


def _dedupe_automated(items: Iterable[AutomatedPolicy]) -> List[AutomatedPolicy]:
    seen: set[int] = set()
    out: List[AutomatedPolicy] = []
    for i in items:
        if i.id and i.id not in seen:
            seen.add(i.id)
            out.append(i)
    return out


class Policies:
    """
    API Manager policy resources, minimal surface for API-scoped policies.
    """

    def __init__(
        self, http: HttpClient, *, logger: Optional[LoggerLike] = None
    ) -> None:
        self._http = http
        self._log = logger or default_logger().child("resources.policies")

    def apply_api_policy(
        self,
        org_id: str,
        env_id: str,
        api_id: int | str,
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Apply a new policy to an API instance.

        Args:
            org_id: The organization ID
            env_id: The environment ID
            api_id: The API instance ID
            payload: Policy configuration payload

        Returns:
            Applied policy details as a dict
        """
        r = self._http.post_json(
            f"/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/apis/{api_id}/policies",
            json_body=payload,
        )
        return r.json() or {}

    def apply_api_policy_template(
        self,
        org_id: str,
        env_id: str,
        api_id: int | str,
        *,
        policy_template_id: str,
        configuration: Optional[Dict[str, Any]] = None,
        disabled: Optional[bool] = None,
        order: Optional[int] = None,
        pointcut_data: Optional[Dict[str, Any]] = None,
        group_id: Optional[str] = None,
        asset_id: Optional[str] = None,
        asset_version: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Apply a policy to an API instance using a policy template.

        Args:
            org_id: The organization ID
            env_id: The environment ID
            api_id: The API instance ID
            policy_template_id: The policy template ID to apply
            configuration: Policy configuration
            disabled: Whether the policy should be disabled
            order: Execution order of the policy
            pointcut_data: Pointcut data for the policy
            group_id: Group ID for the policy template asset (defaults to MuleSoft's group)
            asset_id: Asset ID for the policy template (defaults to policy_template_id)
            asset_version: Version of the policy template asset

        Returns:
            Applied policy details as a dict
        """
        # Default to MuleSoft's standard policy asset group
        if group_id is None:
            group_id = "68ef9520-24e9-4cf2-b2f5-620025690913"  # MuleSoft's policy group

        # Default asset_id to the policy template ID
        if asset_id is None:
            asset_id = policy_template_id

        # Default to a common version if not specified
        if asset_version is None:
            asset_version = "1.4.1"  # Common stable version

        payload: Dict[str, Any] = {
            "policyTemplateId": policy_template_id,
            "groupId": group_id,
            "assetId": asset_id,
            "assetVersion": asset_version,
        }
        if configuration is not None:
            payload["configurationData"] = configuration
        if disabled is not None:
            payload["disabled"] = disabled
        if order is not None:
            payload["order"] = order
        if pointcut_data is not None:
            payload["pointcutData"] = pointcut_data
        return self.apply_api_policy(org_id, env_id, api_id, payload)

    def update_api_policy(
        self,
        org_id: str,
        env_id: str,
        api_id: int | str,
        policy_id: int | str,
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Update an existing API policy.

        Args:
            org_id: The organization ID
            env_id: The environment ID
            api_id: The API instance ID
            policy_id: The ID of the policy to update
            payload: Updated policy configuration

        Returns:
            Updated policy details as a dict
        """
        r = self._http._request(
            "PATCH",
            f"/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/apis/{api_id}/policies/{policy_id}",
            headers={"Content-Type": "application/json"},
            json_body=payload,
        )
        return r.json() or {}

    def delete_api_policy(
        self,
        org_id: str,
        env_id: str,
        api_id: int | str,
        policy_id: int | str,
    ) -> None:
        """
        Delete a policy from an API instance.

        Args:
            org_id: The organization ID
            env_id: The environment ID
            api_id: The API instance ID
            policy_id: The ID of the policy to delete
        """
        self._http._request(
            "DELETE",
            f"/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/apis/{api_id}/policies/{policy_id}",
        )

    def list_api_policies(
        self, org_id: str, env_id: str, api_id: int | str
    ) -> List[Dict[str, Any]]:
        """
        List policies applied to a specific API instance.

        Returns a list of dicts with keys:
        policyId, policyTemplateId, type, order, implementationAsset, configuration.
        """
        r = self._http.get(
            f"/apimanager/api/v1/organizations/{org_id}/environments/{env_id}/apis/{api_id}/policies"
        )
        payload = r.json() or {}
        raw = payload.get("policies")
        if not isinstance(raw, list):
            raw = []

        items: List[ApiPolicy] = []
        for obj in raw:
            if isinstance(obj, dict):
                items.append(_to_api_policy(obj))

        flat = [asdict(x) for x in _dedupe(items)]
        self._log.debug(
            "Listed %d API policies for org=%s env=%s api=%s",
            len(flat),
            org_id,
            env_id,
            api_id,
        )
        return flat

    def list_environment_automated_policies(
        self, org_id: str, env_id: str
    ) -> List[Dict[str, Any]]:
        """
        List automated policies applied at the environment scope.

        Returns a list of dicts with keys:
        id, assetId, assetVersion, order, disabled, configurationData, implementationAssets.
        Filters out items whose ruleOfApplication.environmentId is present and does not match env_id.
        """
        r = self._http.get(
            f"/apimanager/api/v1/organizations/{org_id}/automated-policies",
            params={"environmentId": env_id},
        )
        payload = r.json() or {}
        raw = payload.get("automatedPolicies")
        if not isinstance(raw, list):
            raw = []

        items: List[AutomatedPolicy] = []
        for obj in raw:
            if not isinstance(obj, dict):
                continue
            roa = obj.get("ruleOfApplication") or {}
            roa_env = None
            if isinstance(roa, dict):
                roa_env = roa.get("environmentId")
            if roa_env and str(roa_env) != str(env_id):
                # Defensive filter if server returns other env policies
                continue
            items.append(_to_automated_policy(obj))

        flat = [asdict(x) for x in _dedupe_automated(items)]
        self._log.debug(
            "Listed %d automated policies for org=%s env=%s", len(flat), org_id, env_id
        )
        return flat

    def create_automated_policy(
        self,
        org_id: str,
        env_id: str,
        *,
        group_id: str,
        asset_id: str,
        asset_version: str,
        configuration_data: Optional[Dict[str, Any]] = None,
        order: Optional[int] = None,
        pointcut_data: Optional[Dict[str, Any]] = None,
        rule_of_application: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create an automated policy at the environment scope.

        Automated policies are applied automatically to all APIs in the environment
        that match the rule of application criteria.

        Args:
            org_id: The organization ID
            env_id: The environment ID where the policy will be applied
            group_id: Group ID of the policy asset (MuleSoft's is 68ef9520-24e9-4cf2-b2f5-620025690913)
            asset_id: Asset ID of the policy (e.g., "ip-allowlist", "rate-limiting")
            asset_version: Version of the policy asset (e.g., "1.1.1")
            configuration_data: Policy configuration parameters (varies by policy type)
            order: Execution order of the policy (lower numbers execute first)
            pointcut_data: Optional pointcut configuration for resource-level policies
            rule_of_application: Optional dict with additional ruleOfApplication fields.
                For Mule 4 policies, must include "range" specifying API types.
                Example: {"range": [{"groupId": "mule", "assetId": "http-policy"}]}
                If not provided, defaults to Mule 4 HTTP APIs.

        Returns:
            Dict containing the created automated policy details including:
            - id: The unique identifier of the created policy
            - assetId, assetVersion, groupId
            - configurationData, order, disabled
            - ruleOfApplication with environmentId and organizationId
            - implementationAssets

        Raises:
            HttpError: If the policy creation fails (e.g., 400 for invalid config)

        Example:
            client.policies.create_automated_policy(
                org_id="abc123",
                env_id="def456",
                group_id="68ef9520-24e9-4cf2-b2f5-620025690913",
                asset_id="ip-allowlist",
                asset_version="1.1.1",
                configuration_data={
                    "ipExpression": "#[attributes.headers['x-forwarded-for']]",
                    "ips": ["192.168.1.0/24"]
                },
                order=1,
            )
        """
        # Build ruleOfApplication - only environmentId is required
        # The API will automatically add organizationId
        roa: Dict[str, Any] = {"environmentId": env_id}

        # Merge any additional rule_of_application fields if provided
        if rule_of_application:
            roa.update(rule_of_application)

        payload: Dict[str, Any] = {
            "ruleOfApplication": roa,
            "groupId": group_id,
            "assetId": asset_id,
            "assetVersion": asset_version,
        }

        if configuration_data is not None:
            payload["configurationData"] = configuration_data
        if order is not None:
            payload["order"] = order
        if pointcut_data is not None:
            payload["pointcutData"] = pointcut_data

        r = self._http.post_json(
            f"/apimanager/api/v1/organizations/{org_id}/automated-policies",
            json_body=payload,
        )

        result = r.json() or {}
        self._log.info(
            "Created automated policy %s v%s in org=%s env=%s (id=%s)",
            asset_id,
            asset_version,
            org_id,
            env_id,
            result.get("id"),
        )
        return result

    def get_automated_policy(
        self,
        org_id: str,
        policy_id: int | str,
    ) -> Dict[str, Any]:
        """
        Get a specific automated policy by ID.

        Args:
            org_id: The organization ID
            policy_id: The ID of the automated policy

        Returns:
            Dict containing the automated policy details

        Raises:
            HttpError: If the policy is not found (404)
        """
        r = self._http.get(
            f"/apimanager/api/v1/organizations/{org_id}/automated-policies/{policy_id}",
        )
        return r.json() or {}

    def update_automated_policy(
        self,
        org_id: str,
        policy_id: int | str,
        *,
        configuration_data: Optional[Dict[str, Any]] = None,
        order: Optional[int] = None,
        pointcut_data: Optional[Dict[str, Any]] = None,
        disabled: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """
        Update an existing automated policy.

        This method fetches the current policy, merges in the changes, and sends
        the full updated payload back to the API (which requires all fields).

        Args:
            org_id: The organization ID
            policy_id: The ID of the automated policy to update
            configuration_data: Updated policy configuration parameters
            order: Updated execution order
            pointcut_data: Updated pointcut configuration
            disabled: Whether to disable the policy

        Returns:
            Dict containing the updated automated policy details

        Raises:
            HttpError: If the update fails (e.g., 404 if policy not found)
        """
        # Fetch current policy to get required fields
        current = self.get_automated_policy(org_id, policy_id)

        # Build payload with required fields from current policy
        payload: Dict[str, Any] = {
            "ruleOfApplication": current.get("ruleOfApplication", {}),
            "groupId": current.get("groupId"),
            "assetId": current.get("assetId"),
            "assetVersion": current.get("assetVersion"),
        }

        # Merge in current optional fields, then override with updates
        if current.get("configurationData"):
            payload["configurationData"] = current["configurationData"]
        if current.get("order") is not None:
            payload["order"] = current["order"]
        if current.get("pointcutData"):
            payload["pointcutData"] = current["pointcutData"]
        if current.get("disabled") is not None:
            payload["disabled"] = current["disabled"]

        # Apply updates
        if configuration_data is not None:
            payload["configurationData"] = configuration_data
        if order is not None:
            payload["order"] = order
        if pointcut_data is not None:
            payload["pointcutData"] = pointcut_data
        if disabled is not None:
            payload["disabled"] = disabled

        r = self._http._request(
            "PATCH",
            f"/apimanager/api/v1/organizations/{org_id}/automated-policies/{policy_id}",
            headers={"Content-Type": "application/json"},
            json_body=payload,
        )

        result = r.json() or {}
        self._log.info(
            "Updated automated policy id=%s in org=%s",
            policy_id,
            org_id,
        )
        return result

    def delete_automated_policy(
        self,
        org_id: str,
        policy_id: int | str,
    ) -> None:
        """
        Delete an automated policy.

        Args:
            org_id: The organization ID
            policy_id: The ID of the automated policy to delete

        Raises:
            HttpError: If the delete fails (e.g., 404 if policy not found)
        """
        self._http._request(
            "DELETE",
            f"/apimanager/api/v1/organizations/{org_id}/automated-policies/{policy_id}",
        )

        self._log.info(
            "Deleted automated policy id=%s in org=%s",
            policy_id,
            org_id,
        )
