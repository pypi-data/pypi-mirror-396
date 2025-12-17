# src/anypoint_sdk/collectors/inventory.py
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, Optional, Pattern, Tuple, Union

from .._logging import LoggerLike, default_logger
from ..client import AnypointClient


@dataclass(frozen=True)
class InventoryOptions:
    """
    Options that control how inventory is collected.
    """

    base_path: str = "./mulesoft_scan_output"
    include_environment_policies: bool = True
    include_api_policies: bool = True
    page_limit: int = 500


@dataclass(frozen=True)
class InventoryFilters:
    """
    Inclusive filters. All provided filters are applied conjunctively.

    If `orgs` is explicitly passed to build_inventory, organisation filters here are ignored.
    API filters are always applied.
    """

    # Organisations
    org_ids: Optional[List[str]] = None
    org_names: Optional[List[str]] = None
    org_name_regex: Optional[str] = None
    # APIs
    api_names: Optional[List[str]] = None
    api_name_regex: Optional[str] = None


def _api_name_from_instance(inst: Mapping[str, Any], api_id: int | str) -> str:
    name = (
        inst.get("assetId") or inst.get("exchangeAssetName") or inst.get("name") or ""
    ).strip()
    return name or f"api-{api_id}"


def _as_dict(obj: Any) -> Dict[str, Any]:
    """Return obj if it is a dict, else an empty dict. Helps type checkers."""
    return obj if isinstance(obj, dict) else {}


def _compile_rx(pat: Optional[str]) -> Optional[Pattern[str]]:
    if pat is None:
        return None
    pat = str(pat).strip()
    if not pat:
        return None
    return re.compile(pat)


def _match_list(name: Optional[str], allowed: Optional[List[str]]) -> Optional[bool]:
    if not allowed:
        return None  # no decision
    return bool(name in allowed)


def _match_regex(name: Optional[str], rx: Optional[Pattern[str]]) -> Optional[bool]:
    if rx is None:
        return None
    return bool(name is not None and rx.search(name))


def _org_included(
    org: Dict[str, Any],
    filt: Optional[InventoryFilters],
    org_rx: Optional[Pattern[str]],
) -> bool:
    if not filt:
        return True
    # IDs must match if provided
    if filt.org_ids:
        oid = str(org.get("id", ""))
        if oid not in set(filt.org_ids):
            return False
    # Names and or regex must match if provided
    if filt.org_names:
        if not _match_list(org.get("name"), filt.org_names):
            return False
    if org_rx is not None:
        if not _match_regex(org.get("name"), org_rx):
            return False
    return True


def _api_included(
    inst: Dict[str, Any],
    filt: Optional[InventoryFilters],
    api_rx: Optional[Pattern[str]],
) -> bool:
    if not filt:
        return True
    # Choose a stable API name to test
    name = inst.get("assetId") or inst.get("exchangeAssetName") or inst.get("name")
    if filt.api_names and not _match_list(name, filt.api_names):
        return False
    if api_rx is not None and not _match_regex(name, api_rx):
        return False
    return True


def _first_limit_ms(
    limits: Optional[List[Dict[str, Any]]],
) -> Tuple[Optional[int], Optional[float]]:
    """
    Extract (maximumRequests, time_period_seconds) from the first valid entry.
    """
    if not isinstance(limits, list):
        return None, None
    for it in limits:
        if not isinstance(it, dict):
            continue
        mr = it.get("maximumRequests")
        ms = it.get("timePeriodInMilliseconds")
        if isinstance(mr, int) and isinstance(ms, int):
            return mr, float(ms) / 1000.0
    return None, None


def _pick_runtime_version(
    endpoint: Mapping[str, Any], deployment: Mapping[str, Any]
) -> Optional[str]:
    """
    Prefer endpoint.apiGatewayVersion like "4.9.8", fallback to deployment.gatewayVersion "4.9.8:xyz".
    """
    ver = endpoint.get("apiGatewayVersion")
    if isinstance(ver, str) and ver:
        return ver.split(":")[0]
    g = deployment.get("gatewayVersion")
    if isinstance(g, str) and g:
        return g.split(":")[0]
    return None


def _api_identity_name(detail: Dict[str, Any]) -> Tuple[str, str]:
    # assetId and productVersion form the identity you use
    return str(detail.get("assetId", "")), str(detail.get("productVersion", ""))


def _as_str(v: Any) -> Optional[str]:
    return str(v) if v is not None else None


def _collect_policy_rows_api(policies_payload: Any) -> List[Dict[str, Any]]:
    """
    Normalise API-scoped policies. Accepts either:
      - {"policies": [ ... ]}
      - [ ... ]
    """
    # Extract items defensively
    raw = (
        policies_payload.get("policies")
        if isinstance(policies_payload, dict)
        else policies_payload
    )
    items = raw if isinstance(raw, list) else []

    rows: List[Dict[str, Any]] = []
    for p in items:
        if not isinstance(p, dict):
            continue

        impl = p.get("implementationAsset")
        impl = impl if isinstance(impl, dict) else None

        template = p.get("template")
        template = template if isinstance(template, dict) else None

        cfg = p.get("configuration")
        cfg_dict: Optional[Dict[str, Any]] = cfg if isinstance(cfg, dict) else None

        policy_template_id = p.get("policyTemplateId")
        group_id = (template.get("groupId") if template else None) or (
            impl.get("groupId") if impl else None
        )
        asset_id = (template.get("assetId") if template else None) or (
            impl.get("assetId") if impl else None
        )
        asset_version = (template.get("assetVersion") if template else None) or (
            impl.get("version") if impl else None
        )
        pointcut_data = p.get("pointcutData")
        order = p.get("order")
        disabled = bool(p.get("disabled", False))

        # If there is literally nothing meaningful, skip
        if not any([cfg_dict, asset_id, policy_template_id, pointcut_data, order]):
            continue

        rows.append(
            {
                "policy_name": asset_id,
                "policy_config": cfg_dict,
                "plugin_name": None,
                "plugin_config": None,
                "metadata": {
                    "policy_template_id": policy_template_id,
                    "group_id": group_id,
                    "asset_id": asset_id,
                    "asset_version": asset_version,
                    "disabled": disabled,
                    "order": order,
                    "scope": "api",
                    "pointcut_data": pointcut_data,
                    "created_date": None,  # API policy payloads usually lack audit timestamps
                    "updated_date": None,
                    "source": "anypoint_live_api",
                },
            }
        )

    return rows


def _collect_policy_rows_env(automated_payload: Any) -> List[Dict[str, Any]]:
    """
    Normalise environment automated policies. Accepts either:
      - {"automatedPolicies": [ ... ]}
      - [ ... ]
    """
    # Extract items defensively
    raw = (
        automated_payload.get("automatedPolicies")
        if isinstance(automated_payload, dict)
        else automated_payload
    )
    items = raw if isinstance(raw, list) else []

    rows: List[Dict[str, Any]] = []
    for ap in items:
        if not isinstance(ap, dict):
            continue

        assets = ap.get("implementationAssets")
        assets_list = assets if isinstance(assets, list) else []
        impl = next((a for a in assets_list if isinstance(a, dict)), None)

        cfg = ap.get("configurationData")
        cfg_dict: Optional[Dict[str, Any]] = cfg if isinstance(cfg, dict) else None

        # Skip if there is nothing usable at all
        if impl is None and cfg_dict is None:
            continue

        audit = _as_dict(ap.get("audit"))
        created = _as_dict(audit.get("created")).get("date")
        updated = _as_dict(audit.get("updated")).get("date")

        rows.append(
            {
                "policy_name": impl.get("assetId") if isinstance(impl, dict) else None,
                "policy_config": cfg_dict,
                "plugin_name": None,
                "plugin_config": None,
                "metadata": {
                    "policy_template_id": None,  # not present on env automated payloads
                    "group_id": impl.get("groupId") if isinstance(impl, dict) else None,
                    "asset_id": impl.get("assetId") if isinstance(impl, dict) else None,
                    "asset_version": (
                        impl.get("version") if isinstance(impl, dict) else None
                    ),
                    "disabled": bool(ap.get("disabled", False)),
                    "order": ap.get("order"),
                    "scope": "environment",
                    "pointcut_data": ap.get("pointcutData"),
                    "created_date": created,
                    "updated_date": updated,
                    "source": "anypoint_live_api",
                },
            }
        )

    return rows


def build_inventory(
    client: AnypointClient,
    *,
    orgs: Optional[Union[List[Dict[str, Any]], List[str]]] = None,
    envs_by_org: Optional[Dict[str, List[Dict[str, Any]]]] = None,
    options: Optional[InventoryOptions] = None,
    filters: Optional[InventoryFilters] = None,
    logger: Optional[LoggerLike] = None,
) -> List[Dict[str, Any]]:
    """
    Walk selected organisations and environments, enumerate API instances,
    collect details, policies, contracts, tiers, groups, and applications, and
    return a list of records in the requested shape.

    Scoping rules:
      - If `orgs` is provided, it defines the exact set of organisations to process,
        either as a list of dicts with id and name, or as a list of organisation IDs.
        In this case, organisation filters in `filters` are ignored.
      - If `orgs` is not provided, accessible orgs are discovered and then filtered by
        `filters.org_ids`, `filters.org_names`, and `filters.org_name_regex`.
      - API name filters are always applied.
    """
    log = (logger or default_logger()).child("collector.inventory")
    opts = options or InventoryOptions()
    org_rx = _compile_rx(filters.org_name_regex) if filters else None
    api_rx = _compile_rx(filters.api_name_regex) if filters else None

    # ---------- 1) Determine the exact organisation set ----------
    selected_orgs: List[Dict[str, Any]]
    if orgs is not None:
        if orgs and isinstance(orgs[0], str):
            # orgs is a list of organisation IDs
            wanted_ids = {str(x) for x in orgs}
            try:
                discovered = client.organizations.list_accessible()
            except Exception:
                discovered = []
            by_id = {str(o.get("id")): o for o in discovered if isinstance(o, dict)}
            selected_orgs = [by_id.get(oid, {"id": oid}) for oid in wanted_ids]
        else:
            # orgs is a list of dicts
            selected_orgs = [o for o in orgs if isinstance(o, dict)]
        # Ignore organisation filters when explicit `orgs` passed
    else:
        discovered = client.organizations.list_accessible()
        selected_orgs = [
            o
            for o in discovered
            if isinstance(o, dict) and _org_included(o, filters, org_rx)
        ]

    # Build id -> name map
    org_name = {str(o["id"]): o.get("name") for o in selected_orgs if o.get("id")}
    if not org_name:
        return []

    # ---------- 2) Environments, restricted to selected orgs ----------
    if envs_by_org is None:
        try:
            envs_by_org = client.environments.list_by_orgs(
                selected_orgs, skip_unauthorised=True
            )
        except Exception:
            envs_by_org = {}
    # prune to selected org ids only
    envs_by_org = {oid: (envs_by_org.get(oid, []) or []) for oid in org_name.keys()}

    # ---------- 3) Applications per selected org ----------
    apps_by_org: Dict[str, Dict[int, Dict[str, Any]]] = {}
    for oid in org_name.keys():
        try:
            apps = client.applications.list(oid)
        except Exception as e:
            log.warning("Failed to list applications for org %s, %s", oid, e)
            apps = []
        index: Dict[int, Dict[str, Any]] = {}
        for a in apps:
            if not isinstance(a, dict):
                continue
            try:
                index[int(a["id"])] = a
            except Exception:
                continue
        apps_by_org[oid] = index

    # ---------- 4) Walk orgs and envs ----------
    out: List[Dict[str, Any]] = []
    for org_id, org_nm in org_name.items():
        envs = envs_by_org.get(org_id, [])
        # id -> name map for this org's envs
        env_name_map: Dict[str, Optional[str]] = {}
        for ev in envs:
            if not isinstance(ev, dict):
                continue
            eid = str(ev.get("id", "")).strip()
            if not eid:
                continue
            env_name_map[eid] = str(ev.get("name", "")).strip() or None

        for env in envs:
            if not isinstance(env, dict):
                continue
            env_id = str(env.get("id", "")).strip()
            if not env_id:
                continue

            # List API instances
            try:
                instances_raw = client.apis.list_instances(
                    org_id, env_id, limit=opts.page_limit
                )
            except Exception as e:
                log.warning(
                    "Failed to list APIs for org=%s env=%s, %s", org_id, env_id, e
                )
                continue
            instances_list = (
                [i for i in instances_raw if isinstance(i, dict)]
                if isinstance(instances_raw, list)
                else []
            )

            # Filter by API name if requested
            instances = [i for i in instances_list if _api_included(i, filters, api_rx)]

            for inst in instances:
                api_id = inst.get("id")
                if api_id is None:
                    continue

                # Fetch instance detail
                try:
                    detail = client.apis.get_instance(org_id, env_id, api_id)
                except Exception as e:
                    log.warning(
                        "Failed to get API detail org=%s env=%s api=%s, %s",
                        org_id,
                        env_id,
                        api_id,
                        e,
                    )
                    continue
                if not isinstance(detail, dict):
                    continue

                # Names and versions
                asset_id, product_version = _api_identity_name(detail)
                if not asset_id:
                    asset_id = _api_name_from_instance(inst, api_id)

                # Endpoint and deployment
                endpoint = _as_dict(detail.get("endpoint"))
                deployment = _as_dict(detail.get("deployment"))

                # Group discovery
                try:
                    group_instance_id = client.groups.find_group_for_api(
                        org_id, env_id, api_id
                    )
                except Exception:
                    group_instance_id = None

                # Policies
                policy_rows: List[Dict[str, Any]] = []
                if opts.include_api_policies:
                    try:
                        payload = client.policies.list_api_policies(
                            org_id, env_id, api_id
                        )
                        policy_rows += _collect_policy_rows_api(payload)
                    except Exception as e:
                        log.debug(
                            "API policies not available org=%s env=%s api=%s, %s",
                            org_id,
                            env_id,
                            api_id,
                            e,
                        )
                if opts.include_environment_policies:
                    try:
                        payload = client.policies.list_environment_automated_policies(
                            org_id, env_id
                        )
                        policy_rows += _collect_policy_rows_env(payload)
                    except Exception as e:
                        log.debug(
                            "Environment automated policies not available org=%s env=%s, %s",
                            org_id,
                            env_id,
                            e,
                        )

                # Contracts, joined to applications for credentials
                clients_rows: List[Dict[str, Any]] = []
                try:
                    api_contracts = client.contracts.list_api_contracts(
                        org_id, env_id, api_id
                    )
                except Exception:
                    api_contracts = []
                for c in api_contracts:
                    if not isinstance(c, dict):
                        continue
                    app_id = c.get("applicationId")
                    app = (
                        apps_by_org.get(org_id, {}).get(int(app_id))
                        if app_id is not None
                        else None
                    )
                    clients_rows.append(
                        {
                            "app_id": _as_str(app_id),
                            "app_name": (
                                app.get("name") if app else c.get("applicationName")
                            ),
                            "client_id": app.get("clientId") if app else None,
                            "contract_id": _as_str(c.get("id")),
                            "contract_status": c.get("status"),
                            "sla_tier_name": c.get("tierName") or "",
                            "sla_tier_id": _as_str(c.get("tierId")) or "",
                            "approved_date": c.get("approvedDate"),
                            "created_date": c.get("approvedDate"),
                            "client_secret": app.get("clientSecret") if app else None,
                        }
                    )

                # Group contracts, if any
                if group_instance_id is not None:
                    try:
                        grp_contracts = client.contracts.list_group_contracts(
                            org_id, env_id, group_instance_id
                        )
                    except Exception:
                        grp_contracts = []
                    for c in grp_contracts:
                        if not isinstance(c, dict):
                            continue
                        app_id = c.get("applicationId")
                        app = (
                            apps_by_org.get(org_id, {}).get(int(app_id))
                            if app_id is not None
                            else None
                        )
                        clients_rows.append(
                            {
                                "app_id": _as_str(app_id),
                                "app_name": (
                                    app.get("name") if app else c.get("applicationName")
                                ),
                                "client_id": app.get("clientId") if app else None,
                                "contract_id": _as_str(c.get("id")),
                                "contract_status": c.get("status"),
                                "sla_tier_name": c.get("tierName") or "",
                                "sla_tier_id": _as_str(c.get("tierId")) or "",
                                "approved_date": c.get("approvedDate"),
                                "created_date": c.get("approvedDate"),
                                "contract_type": "group",
                                "group_instance_id": group_instance_id,
                                "client_secret": (
                                    app.get("clientSecret") if app else None
                                ),
                            }
                        )

                # SLA tiers, API scope
                tiers_rows: List[Dict[str, Any]] = []
                try:
                    api_tiers = client.tiers.list_api_tiers(org_id, env_id, api_id)
                except Exception:
                    api_tiers = []
                for t in api_tiers:
                    if not isinstance(t, dict):
                        continue
                    mr, secs = _first_limit_ms(t.get("limits"))
                    tiers_rows.append(
                        {
                            "tier_id": _as_str(t.get("id")),
                            "name": t.get("name"),
                            "description": t.get("description"),
                            "max_requests": mr,
                            "time_period_seconds": secs,
                            "status": t.get("status"),
                            "auto_approve": t.get("autoApprove"),
                            "application_count": t.get("applicationCount"),
                            "scope": "api",
                            "scope_id": _as_str(api_id),
                        }
                    )

                # SLA tiers, group scope
                if group_instance_id is not None:
                    try:
                        grp_tiers = client.tiers.list_group_tiers(
                            org_id, env_id, group_instance_id
                        )
                    except Exception:
                        grp_tiers = []
                    for t in grp_tiers:
                        if not isinstance(t, dict):
                            continue
                        dl = t.get("defaultLimits")
                        mr, secs = _first_limit_ms(dl)
                        if mr is None:
                            lbs = t.get("limitsByApi")
                            if isinstance(lbs, list) and lbs:
                                first = lbs[0]
                                if isinstance(first, dict):
                                    mr, secs = _first_limit_ms(first.get("limits"))
                        tiers_rows.append(
                            {
                                "tier_id": _as_str(t.get("id")),
                                "name": t.get("name"),
                                "description": t.get("description"),
                                "max_requests": mr,
                                "time_period_seconds": secs,
                                "status": t.get("status"),
                                "auto_approve": t.get("autoApprove"),
                                "application_count": t.get("applicationCount"),
                                "scope": "group",
                                "scope_id": group_instance_id,
                                "group_instance_id": group_instance_id,
                            }
                        )

                # Timestamps
                aud = _as_dict(detail.get("audit"))
                created = _as_dict(aud.get("created")).get("date")
                updated = _as_dict(aud.get("updated")).get("date")

                # Final record
                rec = {
                    "api_name": asset_id,
                    "api_version": product_version,
                    "metadata": {
                        "source": "anypoint_live_api",
                        "api_name": asset_id,
                        "api_version": product_version,
                        "base_path": opts.base_path,
                        "anypoint_data": {
                            "api_id": _as_str(api_id),
                            "group_id": detail.get("groupId"),
                            "asset_id": asset_id,
                            "asset_version": detail.get("assetVersion"),
                            "technology": detail.get("technology"),
                            "status": detail.get("status"),
                            "deprecated": detail.get("deprecated"),
                            "endpoint_uri": endpoint.get("uri"),
                            "proxy_uri": endpoint.get("proxyUri"),
                            "deployment_type": deployment.get("type")
                            or endpoint.get("deploymentType"),
                            "is_cloud_hub": endpoint.get("isCloudHub"),
                            "mule_version_4_or_above": endpoint.get(
                                "muleVersion4OrAbove"
                            ),
                            "runtime_version": _pick_runtime_version(
                                endpoint, deployment
                            ),
                            "java_version": (
                                _as_dict(endpoint.get("runtimeMetadata")).get(
                                    "javaVersion"
                                )
                                or _as_dict(deployment.get("targetMetadata")).get(
                                    "javaVersion"
                                )
                            ),
                            "last_active_date": detail.get("lastActiveDate"),
                            "environment_id": env_id,
                            "environment_name": env_name_map.get(env_id),
                            "organization_id": org_id,
                            "organization_name": org_nm,
                            "created_date": created,
                            "updated_date": updated,
                            "client_applications": clients_rows,
                            "sla_tiers": tiers_rows,
                        },
                    },
                    "policy_configurations": policy_rows,
                    "plugin_config_file_path": f"{opts.base_path}/{asset_id}/{product_version}/{asset_id}.yaml",
                    "metadata_file_path": f"{opts.base_path}/{asset_id}/{product_version}/{asset_id}.yaml",
                    "tags": [],
                }

                out.append(rec)

    return out
