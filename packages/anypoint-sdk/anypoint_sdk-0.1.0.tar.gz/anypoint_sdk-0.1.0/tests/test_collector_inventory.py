# tests/test_collector_inventory.py
from __future__ import annotations

import re
import unittest
from typing import Any, Dict, List, Optional

from anypoint_sdk.collectors.inventory import (
    InventoryFilters,
    InventoryOptions,
    _collect_policy_rows_api,
    _compile_rx,
    _first_limit_ms,
    _match_list,
    _match_regex,
    _org_included,
    _pick_runtime_version,
    build_inventory,
)

# -----------------------------
# Minimal fakes for the client
# -----------------------------


class _FakeOrganizations:
    def __init__(self, orgs: List[Dict[str, Any]]) -> None:
        self._orgs = orgs

    def list_accessible(self) -> List[Dict[str, Any]]:
        return list(self._orgs)


class _FakeEnvironments:
    def __init__(self, envs_by_org: Dict[str, List[Dict[str, Any]]]) -> None:
        self._by_org = envs_by_org

    def list_by_orgs(
        self, orgs: List[Dict[str, Any]], *, skip_unauthorised: bool = True
    ) -> Dict[str, List[Dict[str, Any]]]:
        # Return only orgs present in self._by_org to simulate permission gaps
        out: Dict[str, List[Dict[str, Any]]] = {}
        for o in orgs:
            oid = o.get("id")
            if oid in self._by_org:
                out[oid] = list(self._by_org[oid])
        return out


class _FakeApis:
    def __init__(
        self,
        instances: Dict[str, Dict[str, List[Dict[str, Any]]]],
        details: Dict[str, Dict[str, Any]],
    ) -> None:
        # instances[(org_id, env_id)] => [{"id": 123, "assetId": "...", "productVersion": "..."}]
        self._instances = instances
        # details[str(api_id)] => payload
        self._details = details

    def list_instances(
        self, org_id: str, env_id: str, *, limit: int = 200
    ) -> List[Dict[str, Any]]:
        key = f"{org_id}:{env_id}"
        return list(self._instances.get(key, []))

    def get_instance(
        self, org_id: str, env_id: str, api_id: int | str
    ) -> Dict[str, Any]:
        return dict(self._details.get(str(api_id), {}))


class _FakePolicies:
    def __init__(
        self,
        api_policies: Dict[str, List[Dict[str, Any]]],
        env_policies: Dict[str, List[Dict[str, Any]]],
        raise_on_api: bool = False,
        raise_on_env: bool = False,
    ) -> None:
        # api_policies[f"{org}:{env}:{api}"] => [...]
        self._api = api_policies
        # env_policies[f"{org}:{env}"] => [...]
        self._env = env_policies
        self._raise_api = raise_on_api
        self._raise_env = raise_on_env

    def list_api_policies(
        self, org_id: str, env_id: str, api_id: int | str
    ) -> List[Dict[str, Any]]:
        if self._raise_api:
            raise RuntimeError("api policies unavailable")
        return list(self._api.get(f"{org_id}:{env_id}:{api_id}", []))

    def list_environment_automated_policies(
        self, org_id: str, env_id: str
    ) -> List[Dict[str, Any]]:
        if self._raise_env:
            raise RuntimeError("env policies unavailable")
        return list(self._env.get(f"{org_id}:{env_id}", []))


class _FakeContracts:
    def __init__(
        self,
        api_contracts: Dict[str, List[Dict[str, Any]]],
        group_contracts: Dict[str, List[Dict[str, Any]]],
    ) -> None:
        self._api = api_contracts  # key f"{org}:{env}:{api}"
        self._group = group_contracts  # key f"{org}:{env}:{group}"

    def list_api_contracts(
        self, org_id: str, env_id: str, api_id: int | str
    ) -> List[Dict[str, Any]]:
        return list(self._api.get(f"{org_id}:{env_id}:{api_id}", []))

    def list_group_contracts(
        self, org_id: str, env_id: str, group_id: int | str
    ) -> List[Dict[str, Any]]:
        return list(self._group.get(f"{org_id}:{env_id}:{group_id}", []))


class _FakeTiers:
    def __init__(
        self,
        api_tiers: Dict[str, List[Dict[str, Any]]],
        group_tiers: Dict[str, List[Dict[str, Any]]],
    ) -> None:
        self._api = api_tiers  # key f"{org}:{env}:{api}"
        self._group = group_tiers  # key f"{org}:{env}:{group}"

    def list_api_tiers(
        self, org_id: str, env_id: str, api_id: int | str
    ) -> List[Dict[str, Any]]:
        return list(self._api.get(f"{org_id}:{env_id}:{api_id}", []))

    def list_group_tiers(
        self, org_id: str, env_id: str, group_id: int | str
    ) -> List[Dict[str, Any]]:
        return list(self._group.get(f"{org_id}:{env_id}:{group_id}", []))


class _FakeGroups:
    def __init__(self, mapping: Dict[str, Optional[int]]) -> None:
        # mapping[f"{org}:{env}:{api}"] => group_id or None
        self._m = mapping

    def find_group_for_api(
        self, org_id: str, env_id: str, api_id: int | str
    ) -> Optional[int]:
        return self._m.get(f"{org_id}:{env_id}:{api_id}")


class _FakeApplications:
    def __init__(
        self, by_org: Dict[str, List[Dict[str, Any]]], raise_on: Optional[str] = None
    ) -> None:
        self._by_org = by_org
        self._raise_on = set([raise_on]) if raise_on else set()

    def list(self, org_id: str) -> List[Dict[str, Any]]:
        if org_id in self._raise_on:
            raise RuntimeError("apps fail")
        return list(self._by_org.get(org_id, []))


class _FakeClient:
    def __init__(
        self,
        *,
        orgs: List[Dict[str, Any]],
        envs_by_org: Dict[str, List[Dict[str, Any]]],
        api_instances: Dict[str, Dict[str, List[Dict[str, Any]]]],
        api_details: Dict[str, Dict[str, Any]],
        api_policies: Dict[str, List[Dict[str, Any]]] | None = None,
        env_policies: Dict[str, List[Dict[str, Any]]] | None = None,
        api_contracts: Dict[str, List[Dict[str, Any]]] | None = None,
        group_contracts: Dict[str, List[Dict[str, Any]]] | None = None,
        api_tiers: Dict[str, List[Dict[str, Any]]] | None = None,
        group_tiers: Dict[str, List[Dict[str, Any]]] | None = None,
        groups_map: Dict[str, Optional[int]] | None = None,
        apps_by_org: Dict[str, List[Dict[str, Any]]] | None = None,
        apps_raise_on_org: Optional[str] = None,
        policies_raise_api: bool = False,
        policies_raise_env: bool = False,
    ) -> None:
        self.organizations = _FakeOrganizations(orgs)
        self.environments = _FakeEnvironments(envs_by_org)
        self.apis = _FakeApis(api_instances, api_details)
        self.policies = _FakePolicies(
            api_policies or {},
            env_policies or {},
            policies_raise_api,
            policies_raise_env,
        )
        self.contracts = _FakeContracts(api_contracts or {}, group_contracts or {})
        self.tiers = _FakeTiers(api_tiers or {}, group_tiers or {})
        self.groups = _FakeGroups(groups_map or {})
        self.applications = _FakeApplications(
            apps_by_org or {}, raise_on=apps_raise_on_org
        )


class _RaisingPolicies(_FakePolicies):
    def list_api_policies(self, org_id: str, env_id: str, api_id: int | str):
        raise RuntimeError("api policies boom")

    def list_environment_automated_policies(self, org_id: str, env_id: str):
        raise RuntimeError("env policies boom")


class _RaisingGroupContracts(_FakeContracts):
    def list_group_contracts(self, org_id: str, env_id: str, group_id: int | str):
        raise RuntimeError("group contracts down")


class _FunnyGroupTiers(_FakeTiers):
    """First limitsByApi entry is non-dict so isinstance(...) fails."""

    def list_group_tiers(self, org_id: str, env_id: str, group_id: int | str):
        return [
            {
                "id": 909,
                "name": "odd-first",
                "status": "ACTIVE",
                "autoApprove": False,
                "applicationCount": 0,
                "defaultLimits": None,
                "limitsByApi": [
                    123,  # non-dict, forces the 'first = lbs[0]' branch where isinstance(first, dict) is False
                ],
            }
        ]


# class _OnlyIdsNoNamesApis(_FakeApis):
#    """Instances without usable names, to hit the api-{id} fallback."""
#
#    def list_instances(self, org_id: str, env_id: str, *, limit: int = 200):
#        return [{"id": 321}]  # no assetId/name/exchangeAssetName
#
#    def get_instance(self, org_id: str, env_id: str, api_id: int | str):
#        return {"productVersion": "v0", "endpoint": {}, "deployment": {}, "audit": {}}
#


class _RaisingEnvs(_FakeEnvironments):
    def list_by_orgs(self, *a, **k):
        raise RuntimeError("envs down")


class _SomeNonDictApplications(_FakeApplications):
    def list(self, org_id: str):
        # non-dict entry will hit "if not isinstance(a, dict): continue"
        return [123]


class _InstancesMissingIdApis(_FakeApis):
    def list_instances(self, org_id: str, env_id: str, *, limit: int = 200):
        # First item has id=None and should trigger the "continue" at line ~415.
        return [
            {"id": None, "assetId": "ignored"},
            {"id": 999, "assetId": "api-x"},  # valid to ensure we still produce output
        ]

    def get_instance(self, org_id: str, env_id: str, api_id: int | str):
        if int(api_id) == 999:
            return {
                "assetId": "api-x",
                "productVersion": "v0",
                "endpoint": {},
                "deployment": {},
                "audit": {},
            }
        return {}


class _GroupContractsNonDict(_FakeContracts):
    def list_group_contracts(self, org_id: str, env_id: str, group_id: int | str):
        # non-dict row, should "continue" at line ~523
        return [123]


class _ApiTiersNonDict(_FakeTiers):
    def list_api_tiers(self, org_id: str, env_id: str, api_id: int | str):
        # non-dict row, should "continue" at line ~559
        return [123]

    def list_group_tiers(self, org_id: str, env_id: str, group_id: int | str):
        # keep base behaviour for group tiers
        return super().list_group_tiers(org_id, env_id, group_id)


class _GroupTiersNonDict(_FakeTiers):
    def list_group_tiers(self, org_id: str, env_id: str, group_id: int | str):
        # non-dict row, should "continue" at line ~586
        return [123]

    def list_api_tiers(self, org_id: str, env_id: str, api_id: int | str):
        # keep base behaviour for api tiers
        return super().list_api_tiers(org_id, env_id, api_id)


# -----------------------------
# Test cases
# -----------------------------


class InventoryCollectorTests(unittest.TestCase):
    def setUp(self) -> None:
        # Common fixtures
        self.orgs = [
            {"id": "o1", "name": "Org One"},
            {"id": "o2", "name": "Org Two"},
        ]
        self.envs = {
            "o1": [{"id": "e1", "name": "Sandbox"}],
            "o2": [{"id": "e2", "name": "Design"}],
        }
        # One API per env
        self.instances = {
            "o1:e1": [{"id": 101, "assetId": "api-1", "productVersion": "v1"}],
            "o2:e2": [{"id": 201, "assetId": "api-2", "productVersion": "v2"}],
        }
        # Details include endpoint and deployment
        self.details = {
            "101": {
                "assetId": "api-1",
                "productVersion": "v1",
                "assetVersion": "1.0.0",
                "technology": "mule4",
                "status": "active",
                "endpoint": {
                    "uri": "http://httpbin.org",
                    "proxyUri": "http://0.0.0.0:8081/api",
                    "apiGatewayVersion": "4.9.8",
                },
                "deployment": {
                    "type": "CH2",
                    "gatewayVersion": "4.9.8:edge",
                    "targetMetadata": {"javaVersion": "17"},
                },
                "audit": {
                    "created": {"date": "2025-08-13T14:05:28.865Z"},
                    "updated": {"date": "2025-08-15T08:30:12.535Z"},
                },
                "lastActiveDate": "2025-08-16T16:09:40.076Z",
            },
            "201": {
                "assetId": "api-2",
                "productVersion": "v2",
                "assetVersion": "2.0.0",
                "technology": "mule4",
                "status": "active",
                "endpoint": {
                    "uri": "https://httpbin.org",
                    "proxyUri": "http://0.0.0.0:8081/api",
                    "deploymentType": "CH2",
                },
                "deployment": {},
                "audit": {
                    "created": {"date": "2025-08-15T09:16:10.558Z"},
                    "updated": {"date": "2025-08-15T09:17:44.915Z"},
                },
                "lastActiveDate": "2025-08-16T16:09:22.374Z",
            },
        }
        # Policies, contracts, tiers, groups
        self.api_policies = {
            "o1:e1:101": [
                {
                    "policyTemplateId": "348742",
                    "order": 1,
                    "configuration": {
                        "clientIdExpression": "#[...]",
                        "clientSecretExpression": "#[...]",
                    },
                    "template": {
                        "assetId": "rate-limiting-sla-based",
                        "assetVersion": "1.3.0",
                    },
                    "audit": {"created": {}, "updated": {}},
                }
            ]
        }
        self.env_policies = {
            "o1:e1": [
                {
                    "id": 129720,
                    "configurationData": {"ips": ["1.2.3.4/32"]},
                    "implementationAssets": [
                        {
                            "assetId": "ip-allowlist",
                            "groupId": "68ef...",
                            "version": "1.1.1",
                        }
                    ],
                    "order": 2,
                    "disabled": False,
                    "audit": {
                        "created": {"date": "2025-08-13T14:20:55.647Z"},
                        "updated": {"date": "2025-08-15T07:37:38.005Z"},
                    },
                }
            ]
        }
        self.api_contracts = {
            "o1:e1:101": [
                {
                    "id": 7534804,
                    "status": "APPROVED",
                    "approvedDate": "2025-08-14T17:17:30.341Z",
                    "applicationId": 2693438,
                    "applicationName": "fallback-app-name",
                    "tierId": 2247207,
                    "tierName": "gold",
                }
            ]
        }
        self.group_contracts = {
            "o1:e1:368690": [
                {
                    "id": 7535153,
                    "status": "APPROVED",
                    "approvedDate": "2025-08-14T19:12:35.196Z",
                    "applicationId": 2693549,
                    "applicationName": "fallback-app-2",
                    "tierId": 2247208,
                    "tierName": "silver",
                }
            ]
        }
        self.api_tiers = {
            "o1:e1:101": [
                {
                    "id": 2247207,
                    "name": "gold",
                    "description": "gold tier",
                    "limits": [
                        {"maximumRequests": 100, "timePeriodInMilliseconds": 1000}
                    ],
                    "status": "ACTIVE",
                    "autoApprove": False,
                    "applicationCount": 2,
                }
            ]
        }
        self.group_tiers = {
            "o1:e1:368690": [
                {
                    "id": 2248233,
                    "name": "Bronze",
                    "description": "Bronze Tier",
                    "limitsByApi": [
                        {
                            "apiId": 101,
                            "limits": [
                                {
                                    "maximumRequests": 10,
                                    "timePeriodInMilliseconds": 50000,
                                }
                            ],
                        }
                    ],
                    "status": "ACTIVE",
                    "autoApprove": True,
                    "applicationCount": 0,
                },
                {
                    "id": 2247208,
                    "name": "silver",
                    "description": "silver tier",
                    "defaultLimits": [
                        {"maximumRequests": 50, "timePeriodInMilliseconds": 10000}
                    ],
                    "status": "ACTIVE",
                    "autoApprove": True,
                    "applicationCount": 1,
                },
            ]
        }
        self.groups_map = {"o1:e1:101": 368690, "o2:e2:201": None}
        self.apps_by_org = {
            "o1": [
                {
                    "id": 2693438,
                    "name": "my-client-app-2",
                    "clientId": "2dda15c89...",
                    "clientSecret": "52aBed93...",
                },
                {
                    "id": 2693549,
                    "name": "my-client-app-3",
                    "clientId": "7bf72fbb...",
                    "clientSecret": "e7658108...",
                },
            ],
            "o2": [
                {
                    "id": 2693830,
                    "name": "producer-app-1",
                    "clientId": "dbdb62ab...",
                    "clientSecret": "d0F15a81...",
                }
            ],
        }

    def _client(self, **overrides: Any) -> _FakeClient:
        base = {
            "orgs": self.orgs,
            "envs_by_org": self.envs,
            "api_instances": self.instances,
            "api_details": self.details,
            "api_policies": self.api_policies,
            "env_policies": self.env_policies,
            "api_contracts": self.api_contracts,
            "group_contracts": self.group_contracts,
            "api_tiers": self.api_tiers,
            "group_tiers": self.group_tiers,
            "groups_map": self.groups_map,
            "apps_by_org": self.apps_by_org,
        }
        base.update(overrides)
        return _FakeClient(**base)

    # ------------- Tests -------------

    def test_happy_path_builds_records_for_selected_orgs(self) -> None:
        client = self._client()
        # No explicit orgs parameter, filters None, both policy kinds included
        out = build_inventory(client, options=InventoryOptions(), filters=None)
        # We have two APIs in total
        self.assertEqual(len(out), 2)

        # Check key fields for the first API
        r1 = [r for r in out if r["api_name"] == "api-1"][0]
        self.assertEqual(r1["api_version"], "v1")
        meta = r1["metadata"]["anypoint_data"]
        self.assertEqual(meta["environment_name"], "Sandbox")
        self.assertIn("client_applications", meta)
        self.assertGreaterEqual(
            len(meta["client_applications"]), 2
        )  # API + group contracts
        self.assertIn("sla_tiers", meta)
        self.assertGreaterEqual(len(meta["sla_tiers"]), 3)  # one api, two group

        # Policy rows present from both scopes
        self.assertIn("policy_configurations", r1)
        self.assertGreaterEqual(len(r1["policy_configurations"]), 2)

    def test_explicit_org_ids_ignores_org_filters_and_prunes_envs(self) -> None:
        client = self._client()
        # Provide explicit org IDs so organisation filters are ignored
        filters = InventoryFilters(org_names=["Org One"], org_name_regex="^Org")
        out = build_inventory(client, orgs=["o2"], filters=filters)
        # Only Org Two's API should be present
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["metadata"]["anypoint_data"]["organization_id"], "o2")
        self.assertEqual(out[0]["api_name"], "api-2")

    def test_api_filters_by_list_and_regex(self) -> None:
        client = self._client()
        # Only include api-1 using name list, then try regex to include api-2
        out1 = build_inventory(client, filters=InventoryFilters(api_names=["api-1"]))
        self.assertEqual(len(out1), 1)
        self.assertEqual(out1[0]["api_name"], "api-1")

        out2 = build_inventory(
            client, filters=InventoryFilters(api_name_regex=r"^api-2$")
        )
        self.assertEqual(len(out2), 1)
        self.assertEqual(out2[0]["api_name"], "api-2")

    def test_missing_endpoint_and_deployment_are_handled(self) -> None:
        # Make api 201 detail lack endpoint and deployment entirely
        bad_details = dict(self.details)
        bad_details["201"] = {
            "assetId": "api-2",
            "productVersion": "v2",
            "assetVersion": "2.0.0",
            "technology": "mule4",
            "status": "active",
            "audit": {},
        }
        client = self._client(api_details=bad_details)
        out = build_inventory(client, filters=InventoryFilters(api_names=["api-2"]))
        self.assertEqual(len(out), 1)
        anypoint = out[0]["metadata"]["anypoint_data"]
        # runtime_version and java_version should be absent or None, but no exception
        self.assertIsNone(anypoint.get("runtime_version"))
        self.assertIsNone(anypoint.get("java_version"))

    def test_policies_can_be_disabled_and_exceptions_are_ignored(self) -> None:
        client = self._client(policies_raise_api=True, policies_raise_env=True)
        opts = InventoryOptions(
            include_api_policies=False, include_environment_policies=False
        )
        out = build_inventory(
            client, options=opts, filters=InventoryFilters(api_names=["api-1"])
        )
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["policy_configurations"], [])

    def test_applications_list_failure_still_builds_contract_rows(self) -> None:
        # Fail app listing for o1 so contracts fall back to applicationName and no credentials
        client = self._client(apps_raise_on_org="o1")
        out = build_inventory(client, filters=InventoryFilters(api_names=["api-1"]))
        self.assertEqual(len(out), 1)
        clients = out[0]["metadata"]["anypoint_data"]["client_applications"]
        # We will have API and group contracts, but without client_id and client_secret enrichment
        self.assertTrue(all(c.get("client_id") in (None, "") for c in clients))
        self.assertTrue(all(c.get("client_secret") in (None, "") for c in clients))

    def test_envs_by_org_parameter_is_used_and_pruned(self) -> None:
        client = self._client()
        # Supply only o1 in envs_by_org so the o2 API is not traversed
        partial_envs = {"o1": self.envs["o1"]}
        out = build_inventory(client, envs_by_org=partial_envs)
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["metadata"]["anypoint_data"]["organization_id"], "o1")


class InventoryCollectorMoreCoverageTests(InventoryCollectorTests):
    # Reuse setUp() and _client() from InventoryCollectorTests

    def test_explicit_empty_orgs_short_circuits(self) -> None:
        client = self._client()
        out = build_inventory(client, orgs=[])
        self.assertEqual(out, [])  # covers early-return branch

    def test_org_filters_exclude_all(self) -> None:
        client = self._client()
        filters = InventoryFilters(org_names=["No Such Org"], org_name_regex="^Nope$")
        out = build_inventory(client, filters=filters)
        self.assertEqual(out, [])  # covers negative org-name filtering

    def test_envs_by_org_empty_dict_means_no_envs(self) -> None:
        client = self._client()
        out = build_inventory(client, envs_by_org={})
        self.assertEqual(out, [])  # covers branch when supplied env map is empty

    def test_runtime_version_from_deployment_when_endpoint_missing_version(
        self,
    ) -> None:
        bad = dict(self.details)
        # Ensure no apiGatewayVersion on endpoint, but have gatewayVersion on deployment
        bad["201"] = {
            "assetId": "api-2",
            "productVersion": "v2",
            "assetVersion": "2.0.0",
            "technology": "mule4",
            "status": "active",
            "endpoint": {"uri": "https://example.invalid"},  # no apiGatewayVersion
            "deployment": {"gatewayVersion": "4.8.0:foo"},
            "audit": {},
        }
        client = self._client(api_details=bad)
        out = build_inventory(client, filters=InventoryFilters(api_names=["api-2"]))
        self.assertEqual(len(out), 1)
        anypoint = out[0]["metadata"]["anypoint_data"]
        self.assertEqual(
            anypoint.get("runtime_version"), "4.8.0"
        )  # deployment branch taken

    def test_include_api_policies_true_but_provider_raises_is_ignored(self) -> None:
        client = self._client(policies_raise_api=True)
        opts = InventoryOptions(
            include_api_policies=True, include_environment_policies=False
        )
        out = build_inventory(
            client, options=opts, filters=InventoryFilters(api_names=["api-1"])
        )
        self.assertEqual(len(out), 1)
        rows = out[0]["policy_configurations"]
        # No API policies collected due to exception, branch with try/except is executed
        self.assertIsInstance(rows, list)
        self.assertEqual(rows, [])

    def test_include_env_policies_true_but_provider_raises_is_ignored(self) -> None:
        client = self._client(policies_raise_env=True)
        opts = InventoryOptions(
            include_api_policies=False, include_environment_policies=True
        )
        out = build_inventory(
            client, options=opts, filters=InventoryFilters(api_names=["api-1"])
        )
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["policy_configurations"], [])

    def test_no_apis_in_env_returns_empty_for_that_env(self) -> None:
        client = self._client(api_instances={"o1:e1": [], "o2:e2": []})
        out = build_inventory(client)
        self.assertEqual(out, [])  # covers empty-iteration paths

    def test_group_absent_skips_group_contracts_and_tiers(self) -> None:
        client = self._client()
        # Our fixtures map o2:e2:201 -> None, so group lookup branch should skip
        out = build_inventory(client, filters=InventoryFilters(api_names=["api-2"]))
        self.assertEqual(len(out), 1)
        anypoint = out[0]["metadata"]["anypoint_data"]
        self.assertEqual(
            anypoint.get("client_applications"), []
        )  # no API or group contracts in fixtures
        self.assertEqual(anypoint.get("sla_tiers"), [])  # no API or group tiers either

    def test_app_enrichment_populates_client_credentials_when_available(self) -> None:
        client = self._client()
        out = build_inventory(client, filters=InventoryFilters(api_names=["api-1"]))
        self.assertEqual(len(out), 1)
        clients = out[0]["metadata"]["anypoint_data"]["client_applications"]
        # We expect at least one row to have client_id and client_secret from applications list
        self.assertTrue(any(c.get("client_id") for c in clients))
        self.assertTrue(any(c.get("client_secret") for c in clients))

    def test_api_negative_name_filter_regex(self) -> None:
        client = self._client()
        out = build_inventory(
            client, filters=InventoryFilters(api_name_regex=r"^no-match$")
        )
        self.assertEqual(out, [])  # covers negative API-name regex path

    def test_unknown_explicit_org_id_yields_no_results(self) -> None:
        client = self._client()
        out = build_inventory(client, orgs=["does-not-exist"])
        self.assertEqual(out, [])  # covers pruning of unknown org ids

    def test_policy_rows_present_when_both_sources_enabled(self) -> None:
        client = self._client()
        opts = InventoryOptions(
            include_api_policies=True, include_environment_policies=True
        )
        out = build_inventory(
            client, options=opts, filters=InventoryFilters(api_names=["api-1"])
        )
        self.assertEqual(len(out), 1)
        rows = out[0]["policy_configurations"]
        # From fixtures we expect at least two rows, one API policy and one env policy
        self.assertGreaterEqual(len(rows), 2)

    def test_file_paths_are_built_from_base_path(self) -> None:
        client = self._client()
        opts = InventoryOptions(base_path="./scan_out")
        out = build_inventory(
            client, options=opts, filters=InventoryFilters(api_names=["api-1"])
        )
        self.assertEqual(len(out), 1)
        rec = out[0]
        self.assertIn("./scan_out/api-1/v1/api-1.yaml", rec["plugin_config_file_path"])
        self.assertIn("./scan_out/api-1/v1/api-1.yaml", rec["metadata_file_path"])


# -----------------------------
# Helper function coverage
# -----------------------------


class InventoryCollectorHelperEdgeTests(unittest.TestCase):
    def test_compile_rx_none_and_blank(self) -> None:
        self.assertIsNone(_compile_rx(None))
        self.assertIsNone(_compile_rx(""))
        self.assertIsNone(_compile_rx("   "))

    def test_compile_rx_valid(self) -> None:
        rx = _compile_rx(r"^api")
        self.assertIsInstance(rx, re.Pattern)
        self.assertTrue(rx.search("api-1"))

    def test_match_list_returns_none_when_not_provided(self) -> None:
        self.assertIsNone(_match_list("x", None))
        self.assertIsNone(_match_list("x", []))  # falsy means no decision

    def test_match_list_true_and_false(self) -> None:
        self.assertTrue(_match_list("x", ["a", "x", "b"]))
        self.assertFalse(_match_list("x", ["a", "b"]))

    def test_match_regex_none_and_valid(self) -> None:
        self.assertIsNone(_match_regex("name", None))
        rx = re.compile(r"^ab")
        self.assertTrue(_match_regex("abc", rx))
        self.assertFalse(_match_regex("z", rx))

    def test_first_limit_ms_non_list_and_bad_items(self) -> None:
        mr, secs = _first_limit_ms(None)
        self.assertEqual((mr, secs), (None, None))
        mr, secs = _first_limit_ms(["not-a-dict"])
        self.assertEqual((mr, secs), (None, None))

    def test_first_limit_ms_first_valid_pair(self) -> None:
        mr, secs = _first_limit_ms(
            [
                {"foo": "bar"},
                {"maximumRequests": 50, "timePeriodInMilliseconds": 5000},
                {"maximumRequests": 99, "timePeriodInMilliseconds": 9900},
            ]
        )
        self.assertEqual(mr, 50)
        self.assertEqual(secs, 5.0)

    def test_pick_runtime_version_endpoint_precedence(self) -> None:
        ver = _pick_runtime_version(
            {"apiGatewayVersion": "4.9.8:edge"}, {"gatewayVersion": "4.8.0:suffix"}
        )
        self.assertEqual(ver, "4.9.8")

    def test_pick_runtime_version_deployment_fallback_and_none(self) -> None:
        ver = _pick_runtime_version({}, {"gatewayVersion": "4.8.0:xyz"})
        self.assertEqual(ver, "4.8.0")
        ver2 = _pick_runtime_version({}, {})
        self.assertIsNone(ver2)


# -----------------------------
# More inventory edge coverage
# -----------------------------


class _RaisingOrganizations:
    def list_accessible(self):
        raise RuntimeError("boom")


class _ApisThatRaise(_FakeApis):
    def __init__(self, *a, raise_on_list=None, raise_on_get=None, **k):
        super().__init__(*a, **k)
        self._raise_on_list = set(raise_on_list or [])
        self._raise_on_get = set(raise_on_get or [])

    def list_instances(self, org_id: str, env_id: str, *, limit: int = 200):
        key = f"{org_id}:{env_id}"
        if key in self._raise_on_list:
            raise RuntimeError("list failed")
        return super().list_instances(org_id, env_id, limit=limit)

    def get_instance(self, org_id: str, env_id: str, api_id: int | str):
        key = f"{org_id}:{env_id}:{api_id}"
        if key in self._raise_on_get:
            raise RuntimeError("get failed")
        return super().get_instance(org_id, env_id, api_id)


class InventoryCollectorEvenMoreCoverageTests(InventoryCollectorTests):
    # Reuse setUp and _client

    def test_explicit_org_ids_with_discovery_failure_still_scopes(self) -> None:
        client = self._client()
        # Swap in an orgs provider that raises to hit the exception branch
        client.organizations = _RaisingOrganizations()
        out = build_inventory(client, orgs=["o1"])  # explicit ids path
        # Envs come from client.environments, so we still get results for o1
        # unless pruned by envs_by_org. Our base envs include o1:e1 with 101.
        # However applications and other lookups still work.
        self.assertTrue(
            all(r["metadata"]["anypoint_data"]["organization_id"] == "o1" for r in out)
        )

    def test_list_instances_raises_is_logged_and_skipped(self) -> None:
        # Make list_instances raise for o1:e1
        apis = _ApisThatRaise(self.instances, self.details, raise_on_list={"o1:e1"})
        client = self._client()
        client.apis = apis
        out = build_inventory(client)
        # Only o2:e2 should contribute
        self.assertTrue(
            all(r["metadata"]["anypoint_data"]["organization_id"] == "o2" for r in out)
        )

    def test_get_instance_raises_skips_api(self) -> None:
        apis = _ApisThatRaise(self.instances, self.details, raise_on_get={"o1:e1:101"})
        client = self._client()
        client.apis = apis
        out = build_inventory(client)
        # We should only see the api from o2:e2
        names = {r["api_name"] for r in out}
        self.assertEqual(names, {"api-2"})

    def test_unknown_app_id_falls_back_to_application_name(self) -> None:
        # Provide a contract whose applicationId is not present in apps_by_org
        api_contracts = {
            "o1:e1:101": [
                {
                    "id": 999001,
                    "status": "APPROVED",
                    "approvedDate": "x",
                    "applicationId": 424242,
                    "applicationName": "fallback",
                    "tierId": 1,
                    "tierName": "n/a",
                }
            ]
        }
        client = self._client(api_contracts=api_contracts)
        out = build_inventory(client, filters=InventoryFilters(api_names=["api-1"]))
        self.assertEqual(len(out), 1)
        clients = out[0]["metadata"]["anypoint_data"]["client_applications"]
        row = [c for c in clients if c["contract_id"] == "999001"][0]
        self.assertEqual(row["app_name"], "fallback")
        self.assertIsNone(row.get("client_id"))
        self.assertIsNone(row.get("client_secret"))

    def test_group_tiers_no_default_and_no_limits_by_api(self) -> None:
        # Override group tiers to include an item with neither defaultLimits nor limitsByApi
        group_tiers = {
            "o1:e1:368690": [
                {
                    "id": 123,
                    "name": "Odd",
                    "description": "",
                    "status": "ACTIVE",
                    "autoApprove": False,
                    "applicationCount": 0,
                }
            ]
        }
        client = self._client(group_tiers=group_tiers)
        out = build_inventory(client, filters=InventoryFilters(api_names=["api-1"]))
        tiers = out[0]["metadata"]["anypoint_data"]["sla_tiers"]
        # Find our "Odd" tier, should have max_requests/time_period_seconds as None
        odd = [t for t in tiers if t["name"] == "Odd"][0]
        self.assertIsNone(odd["max_requests"])
        self.assertIsNone(odd["time_period_seconds"])

    def test_audit_shapes_missing_created_and_updated(self) -> None:
        bad = dict(self.details)
        bad["101"] = {
            "assetId": "api-1",
            "productVersion": "v1",
            "assetVersion": "1.0.0",
            "technology": "mule4",
            "status": "active",
            "endpoint": {},
            "deployment": {},
            "audit": {"created": "not-a-dict"},  # created not a dict, updated missing
        }
        client = self._client(api_details=bad)
        out = build_inventory(client, filters=InventoryFilters(api_names=["api-1"]))
        meta = out[0]["metadata"]["anypoint_data"]
        self.assertIsNone(meta.get("created_date"))
        self.assertIsNone(meta.get("updated_date"))

    def test_instances_with_name_fallbacks_for_filtering(self) -> None:
        # Use exchangeAssetName and name fallbacks to drive _api_included branches
        instances = {
            "o1:e1": [
                {"id": 1001, "exchangeAssetName": "ex-api", "productVersion": "v1"},
                {"id": 1002, "name": "plain-name", "productVersion": "v1"},
            ]
        }
        details = {
            "1001": {
                "assetId": "ex-api",
                "productVersion": "v1",
                "endpoint": {},
                "deployment": {},
                "audit": {},
            },
            "1002": {
                "assetId": "plain-name",
                "productVersion": "v1",
                "endpoint": {},
                "deployment": {},
                "audit": {},
            },
        }
        client = self._client(
            api_instances=instances,
            api_details=details,
            api_policies={},
            env_policies={},
            api_contracts={},
            group_contracts={},
            api_tiers={},
            group_tiers={},
            groups_map={},
            apps_by_org={},
        )
        # Include only ex-api via regex
        out1 = build_inventory(
            client, filters=InventoryFilters(api_name_regex=r"^ex-api$")
        )
        self.assertEqual({r["api_name"] for r in out1}, {"ex-api"})
        # Include only plain-name via list
        out2 = build_inventory(
            client, filters=InventoryFilters(api_names=["plain-name"])
        )
        self.assertEqual({r["api_name"] for r in out2}, {"plain-name"})

    def test_env_policy_payload_as_dict_and_list_paths_are_supported(self) -> None:
        # Ensure both list and dict payload shapes are handled
        env_policies_list = {
            "o1:e1": [
                {
                    "implementationAssets": [
                        {"assetId": "ip-allowlist", "groupId": "g", "version": "1.1.1"}
                    ],
                    "configurationData": {"ips": []},
                    "order": 1,
                    "disabled": False,
                    "audit": {},
                }
            ]
        }
        client = self._client(env_policies=env_policies_list)
        out = build_inventory(client, filters=InventoryFilters(api_names=["api-1"]))
        self.assertGreaterEqual(len(out[0]["policy_configurations"]), 1)

        # Now return dict shape from provider by swapping the fake
        class _PoliciesDict(_FakePolicies):
            def list_environment_automated_policies(self, org_id, env_id):
                return {
                    "automatedPolicies": super().list_environment_automated_policies(
                        org_id, env_id
                    )
                }

        client = self._client()
        client.policies = _PoliciesDict(self.api_policies, self.env_policies)
        out2 = build_inventory(client, filters=InventoryFilters(api_names=["api-1"]))
        self.assertGreaterEqual(len(out2[0]["policy_configurations"]), 2)

    def test_api_tiers_limits_non_list_branch(self) -> None:
        api_tiers = {
            "o1:e1:101": [
                {
                    "id": 1,
                    "name": "t",
                    "limits": "not-a-list",
                    "status": "ACTIVE",
                    "autoApprove": False,
                    "applicationCount": 0,
                }
            ]
        }
        client = self._client(api_tiers=api_tiers)  # keep existing group tiers
        out = build_inventory(client, filters=InventoryFilters(api_names=["api-1"]))
        tiers = out[0]["metadata"]["anypoint_data"]["sla_tiers"]
        # Find our injected API tier and assert its computed fields
        t = next(x for x in tiers if x["name"] == "t")
        self.assertIsNone(t["max_requests"])
        self.assertIsNone(t["time_period_seconds"])

    def test_envs_by_org_pruning_when_selected_orgs_explicit_dicts(self) -> None:
        client = self._client()
        # Only provide org dict for o2 so o1 envs are pruned
        out = build_inventory(client, orgs=[{"id": "o2", "name": "Two"}])
        self.assertTrue(
            all(r["metadata"]["anypoint_data"]["organization_id"] == "o2" for r in out)
        )


# ================================
# Extra edge coverage for inventory
# ================================


class _WeirdApis(_FakeApis):
    """Return non-list and junk rows to exercise normalisation and skips."""

    def list_instances(self, org_id: str, env_id: str, *, limit: int = 200):
        if f"{org_id}:{env_id}" == "o1:e1":
            return "not-a-list"  # coerced to []
        return super().list_instances(org_id, env_id, limit=limit)


class _WeirdEnvironments(_FakeEnvironments):
    """Return mixed entries, including non-dicts and dicts without id/name."""

    def list_by_orgs(self, orgs, *, skip_unauthorised: bool = True):
        out = super().list_by_orgs(orgs, skip_unauthorised=skip_unauthorised)
        # Corrupt o1 with mixed rubbish
        out["o1"] = [
            {"id": "", "name": "NoId"},  # missing id branch
            {"name": "AlsoBad"},  # no id key
            123,  # non-dict
            {"id": "e1", "name": "Sandbox"},  # one good item to keep traversal alive
        ]
        return out


class _ExplodingGroups(_FakeGroups):
    def find_group_for_api(self, org_id: str, env_id: str, api_id: int | str):
        raise RuntimeError("groups blew up")


class _ApisMissingNames(_FakeApis):
    """Instances with no assetId, exchangeAssetName or name to trigger name fallback paths."""

    def list_instances(self, org_id: str, env_id: str, *, limit: int = 200):
        return [{"id": 321}, {"id": 654, "assetId": ""}]  # both missing usable names

    def get_instance(self, org_id: str, env_id: str, api_id: int | str):
        # Minimal details, missing endpoint/deployment too
        return {"productVersion": "v0", "audit": {}}


class _WeirdPolicies(_FakePolicies):
    """Return weird payload shapes for policy collectors."""

    def list_api_policies(self, org_id: str, env_id: str, api_id: int | str):
        # Return dict with 'policies' set to non-list, then a list with non-dict members
        return {"policies": "nope"}  # will normalise to []

    def list_environment_automated_policies(self, org_id: str, env_id: str):
        # Return a list with a junk item so it's skipped
        return ["junk", {"implementationAssets": "x"}]


class _WeirdContracts(_FakeContracts):
    """Return non-dict rows and rows missing fields to trigger fallbacks."""

    def list_api_contracts(self, org_id: str, env_id: str, api_id: int | str):
        return [
            "bad",  # skipped
            {
                "id": 555,
                "status": "APPROVED",
                "applicationName": "only-name",
            },  # no ids/tiers
        ]

    def list_group_contracts(self, org_id: str, env_id: str, group_id: int | str):
        return [
            {
                "id": 777,
                "status": "APPROVED",
                "applicationId": None,
                "application": {"id": 999, "name": "indirect"},
            }
        ]


class _WeirdTiers(_FakeTiers):
    """Return tier items missing both limits and limitsByApi / defaultLimits."""

    def list_api_tiers(self, org_id: str, env_id: str, api_id: int | str):
        return [
            {
                "id": 901,
                "name": "odd-api",
                "status": "ACTIVE",
                "autoApprove": False,
                "applicationCount": 0,
            }
        ]

    def list_group_tiers(self, org_id: str, env_id: str, group_id: int | str):
        return [
            {
                "id": 902,
                "name": "odd-group",
                "status": "ACTIVE",
                "autoApprove": False,
                "applicationCount": 0,
            }
        ]


class _AppsMissingFields(_FakeApplications):
    """Return application rows without id/credentials to hit enrichment fallbacks."""

    def list(self, org_id: str):
        return [
            {"name": "nameless-creds-missing"},
            {"id": 0, "clientId": "", "clientSecret": ""},  # truthy checks
        ]


class InventoryCollectorPatchEdgeTests(InventoryCollectorTests):
    def test_envs_by_org_mixed_entries_are_filtered(self) -> None:
        client = self._client()
        client.environments = _WeirdEnvironments(self.envs)
        out = build_inventory(client, filters=InventoryFilters(api_names=["api-1"]))
        # Still produces records thanks to the one valid env
        self.assertGreaterEqual(len(out), 1)
        # Ensure bad envs did not break traversal
        self.assertTrue(
            all(r["metadata"]["anypoint_data"]["environment_id"] for r in out)
        )

    def test_instances_non_list_and_junk_rows_are_skipped(self) -> None:
        client = self._client()
        client.apis = _WeirdApis(self.instances, self.details)
        # With o1:e1 returning "not-a-list", only o2:e2 contributes
        out = build_inventory(client)
        self.assertTrue(
            all(r["metadata"]["anypoint_data"]["organization_id"] == "o2" for r in out)
        )

    def test_groups_find_raises_is_ignored(self) -> None:
        client = self._client()
        client.groups = _ExplodingGroups({})
        out = build_inventory(client, filters=InventoryFilters(api_names=["api-1"]))
        # Build continues without group contracts/tiers
        # anypoint = out[0]["metadata"]["anypoint_data"]
        # self.assertEqual(anypoint.get("sla_tiers"), [])
        # self.assertEqual(anypoint.get("client_applications"), [])
        anypoint = out[0]["metadata"]["anypoint_data"]
        tiers = anypoint.get("sla_tiers", [])
        self.assertTrue(all(t.get("scope") != "group" for t in tiers))

    def test_instances_missing_all_names_trigger_fallback(self) -> None:
        client = self._client()
        client.apis = _ApisMissingNames({}, {})  # unused dicts
        # Restrict to org/env where traversal will occur
        envs = {"o1": [{"id": "e1", "name": "Sandbox"}]}
        out = build_inventory(client, orgs=["o1"], envs_by_org=envs)
        # The builder should still yield records, with fallback name like "api-321"
        names = {r["api_name"] for r in out}
        self.assertIn("api-321", names)

    def test_policy_collectors_weird_payloads_do_not_crash(self) -> None:
        client = self._client()
        client.policies = _WeirdPolicies({}, {})
        opts = InventoryOptions(
            include_api_policies=True, include_environment_policies=True
        )
        out = build_inventory(
            client, options=opts, filters=InventoryFilters(api_names=["api-1"])
        )
        # No valid policies collected, but no exception and field present
        self.assertEqual(out[0]["policy_configurations"], [])

    def test_contracts_weird_rows_fallbacks_and_dedup(self) -> None:
        client = self._client()
        client.contracts = _WeirdContracts({}, {})
        client.groups = _FakeGroups({"o1:e1:101": 368690})
        client.tiers = _FakeTiers({}, {})  # neutral tiers
        out = build_inventory(client, filters=InventoryFilters(api_names=["api-1"]))
        apps = out[0]["metadata"]["anypoint_data"]["client_applications"]
        # The 'only-name' row should appear with missing credentials
        r = next(a for a in apps if a["app_name"] == "only-name")
        self.assertIsNone(r.get("client_id"))
        self.assertIsNone(r.get("client_secret"))

    def test_tiers_without_limits_anywhere_result_in_none_metrics(self) -> None:
        client = self._client()
        client.tiers = _WeirdTiers({}, {})
        client.groups = _FakeGroups({"o1:e1:101": 368690})
        out = build_inventory(client, filters=InventoryFilters(api_names=["api-1"]))
        tiers = out[0]["metadata"]["anypoint_data"]["sla_tiers"]
        names = {t["name"] for t in tiers}
        self.assertTrue({"odd-api", "odd-group"}.issubset(names))
        for t in tiers:
            if t["name"] in ("odd-api", "odd-group"):
                self.assertIsNone(t["max_requests"])
                self.assertIsNone(t["time_period_seconds"])

    def test_applications_missing_fields_do_not_break_enrichment(self) -> None:
        client = self._client()
        client.applications = _AppsMissingFields({})
        out = build_inventory(client, filters=InventoryFilters(api_names=["api-1"]))
        clients = out[0]["metadata"]["anypoint_data"]["client_applications"]
        # Rows are present, but enrichment could not fill credentials
        self.assertTrue(all(c.get("client_id") in (None, "") for c in clients))
        self.assertTrue(all(c.get("client_secret") in (None, "") for c in clients))

    def test_base_path_empty_string_still_builds_paths(self) -> None:
        client = self._client()
        opts = InventoryOptions(base_path="")
        out = build_inventory(
            client, options=opts, filters=InventoryFilters(api_names=["api-1"])
        )
        rec = out[0]
        # Paths will start with "/api-name/..." or just "api-name/..." depending on your join logic
        self.assertIn("api-1/v1/api-1.yaml", rec["plugin_config_file_path"])
        self.assertIn("api-1/v1/api-1.yaml", rec["metadata_file_path"])

    def test_org_dict_without_name_and_missing_id_are_skipped_by_explicit_orgs(
        self,
    ) -> None:
        client = self._client()
        # One dict without id should be ignored, one bare string ok
        out = build_inventory(client, orgs=[{"name": "NoId"}, "o1"])
        self.assertTrue(
            all(r["metadata"]["anypoint_data"]["organization_id"] == "o1" for r in out)
        )


class _RaisingApplications(_FakeApplications):
    def list(self, org_id: str):
        raise RuntimeError("apps fail")


class _BadIdApplications(_FakeApplications):
    def list(self, org_id: str):
        # Will hit the int(...) cast exception path and continue
        return [{"id": "not-an-int", "name": "bad"}]


class _DetailNotDictApis(_FakeApis):
    def get_instance(self, org_id: str, env_id: str, api_id: int | str):
        return "not-a-dict"  # causes detail-skip branch


class _NoGroupGroups(_FakeGroups):
    def find_group_for_api(self, org_id: str, env_id: str, api_id: int | str):
        return None  # skip all group branches


class _RaisingContracts(_FakeContracts):
    def list_api_contracts(self, org_id: str, env_id: str, api_id: int | str):
        raise RuntimeError("contracts down")


class _RaisingApiTiers(_FakeTiers):
    def list_api_tiers(self, org_id: str, env_id: str, api_id: int | str):
        raise RuntimeError("api tiers down")


class _RaisingGroupTiers(_FakeTiers):
    def list_group_tiers(self, org_id: str, env_id: str, group_id: int | str):
        raise RuntimeError("group tiers down")


class _JavaMetaWeirdApis(_FakeApis):
    def get_instance(self, org_id: str, env_id: str, api_id: int | str):
        # endpoint.runtimeMetadata and deployment.targetMetadata are not dicts
        base = dict(self._details[str(api_id)])
        base["endpoint"] = {"runtimeMetadata": "weird"}  # not a dict
        base["deployment"] = {"targetMetadata": "also-weird"}  # not a dict
        return base


class _OnlyIdsNoNamesApis(_FakeApis):
    def list_instances(self, org_id: str, env_id: str, *, limit: int = 200):
        # instances with no assetId/name/exchangeAssetName, to drive fallback api-{id}
        return [{"id": 321}, {"id": 654, "assetId": ""}]

    def get_instance(self, org_id: str, env_id: str, api_id: int | str):
        # minimal valid detail to allow record creation
        return {
            "assetId": "",
            "productVersion": "v0",
            "endpoint": {},
            "deployment": {},
            "audit": {},
        }


class InventoryCollectorCoverageFinishTests(InventoryCollectorTests):
    # 1) Early return when selected orgs map to empty id set
    def test_returns_empty_when_selected_org_dicts_have_no_ids(self) -> None:
        client = self._client()
        out = build_inventory(client, orgs=[{"name": "No Id Here"}])
        self.assertEqual(out, [])

    # 2) Provided envs_by_org is pruned to selected org ids
    def test_envs_by_org_pruning_with_extra_keys(self) -> None:
        client = self._client()
        envs_by_org = {
            "oX": [{"id": "eX", "name": "Ignored"}],
            "o1": [{"id": "e1", "name": "Sandbox"}],
        }
        out = build_inventory(
            client, orgs=[{"id": "o1", "name": "One"}], envs_by_org=envs_by_org
        )
        # Only data for o1 should appear
        self.assertTrue(
            all(r["metadata"]["anypoint_data"]["organization_id"] == "o1" for r in out)
        )

    # 3) Applications list raises, branch logs warning and proceeds
    def test_applications_list_raises_warning(self) -> None:
        client = self._client()
        client.applications = _RaisingApplications(
            {}
        )  # forces applications.list(...) to raise

        out = build_inventory(client, filters=InventoryFilters(api_names=["api-1"]))

        apps = out[0]["metadata"]["anypoint_data"]["client_applications"]
        # Contracts are still collected, only enrichment is missing
        self.assertGreater(len(apps), 0)

        # Since applications listing failed, no credentials could be joined
        self.assertTrue(all(a.get("client_id") is None for a in apps))
        self.assertTrue(all(a.get("client_secret") is None for a in apps))

        # And the contract fields are still present
        self.assertTrue(all(a.get("contract_id") for a in apps))
        self.assertTrue(all("contract_status" in a for a in apps))

    # 4) Applications contain bad id that fails int conversion
    def test_application_bad_id_is_skipped(self) -> None:
        client = self._client()
        client.applications = _BadIdApplications({})
        out = build_inventory(client, filters=InventoryFilters(api_names=["api-1"]))
        self.assertGreaterEqual(len(out), 1)  # still builds

    # 5) Instance detail not a dict, skips that API
    def test_detail_not_dict_is_skipped(self) -> None:
        client = self._client()
        client.apis = _DetailNotDictApis(self.instances, self.details)
        out = build_inventory(client)
        # Only o2:e2 contributes since o1:e1 detail is bad
        self.assertTrue(
            all(r["metadata"]["anypoint_data"]["organization_id"] == "o2" for r in out)
        )

    # 6) Options exclude both policy collections, skip branches
    def test_options_exclude_policies(self) -> None:
        client = self._client()
        opts = InventoryOptions(
            include_api_policies=False, include_environment_policies=False
        )
        out = build_inventory(
            client, options=opts, filters=InventoryFilters(api_names=["api-1"])
        )
        self.assertEqual(out[0]["policy_configurations"], [])

    # 7) Contracts list raises, results in empty clients array
    def test_api_contracts_raise_are_skipped(self) -> None:
        client = self._client()
        client.contracts = _RaisingContracts({}, {})
        out = build_inventory(client, filters=InventoryFilters(api_names=["api-1"]))
        self.assertEqual(out[0]["metadata"]["anypoint_data"]["client_applications"], [])

    # 8) No group match path, group branches skipped
    def test_no_group_instance_skips_group_paths(self) -> None:
        client = self._client()
        client.groups = _NoGroupGroups({})
        out = build_inventory(client, filters=InventoryFilters(api_names=["api-1"]))
        tiers = out[0]["metadata"]["anypoint_data"]["sla_tiers"]
        self.assertTrue(all(t["scope"] != "group" for t in tiers))

    # 9) API tiers call raises, branch to empty api tiers
    def test_api_tiers_call_raises(self) -> None:
        client = self._client()
        client.tiers = _RaisingApiTiers({}, {})
        out = build_inventory(client, filters=InventoryFilters(api_names=["api-1"]))
        tiers = out[0]["metadata"]["anypoint_data"]["sla_tiers"]
        # Should contain only group tiers from base fixtures
        self.assertTrue(all(t["scope"] == "group" for t in tiers))

    # 10) Group tiers call raises, branch to empty group tiers
    def test_group_tiers_call_raises(self) -> None:
        client = self._client()
        client.groups = _FakeGroups({"o1:e1:101": 368690})
        client.tiers = _RaisingGroupTiers({}, {})
        out = build_inventory(client, filters=InventoryFilters(api_names=["api-1"]))
        tiers = out[0]["metadata"]["anypoint_data"]["sla_tiers"]
        self.assertTrue(all(t["scope"] == "api" for t in tiers))

    # 11) Java version extraction when runtimeMetadata/targetMetadata are not dicts
    def test_java_version_when_meta_not_dict(self) -> None:
        client = self._client()
        client.apis = _JavaMetaWeirdApis(self.instances, self.details)
        out = build_inventory(client, filters=InventoryFilters(api_names=["api-1"]))
        meta = out[0]["metadata"]["anypoint_data"]
        self.assertIsNone(meta["java_version"])

    # 12) Name fallback when no assetId/name/exchangeAssetName in instance
    def test_instance_name_fallback_api_id(self) -> None:
        client = self._client()
        client.apis = _OnlyIdsNoNamesApis({}, {})
        envs = {"o1": [{"id": "e1", "name": "Sandbox"}]}
        out = build_inventory(
            client, orgs=[{"id": "o1", "name": "One"}], envs_by_org=envs
        )
        names = {r["api_name"] for r in out}
        self.assertIn("api-321", names)


class InventoryCollectorFinalBranches(InventoryCollectorTests):
    # Covers: orgs provided as IDs, not present in discovered list, fallback stub dict (lines ~84-86, 89->91, 92-93)
    def test_orgs_ids_unknown_uses_fallback_stub(self) -> None:
        client = self._client()
        # Provide envs for an unknown org so traversal can proceed
        envs_by_org = {"oz": [{"id": "ez", "name": "Edge"}]}
        # Instances with no names to exercise api-{id} fallback later too
        client.apis = _OnlyIdsNoNamesApis({}, {})
        out = build_inventory(
            client,
            orgs=["oz"],  # unknown to discovered, so fallback {"id":"oz"}
            envs_by_org=envs_by_org,
            filters=InventoryFilters(),  # filters ignored when orgs is explicit
        )
        self.assertTrue(
            all(r["metadata"]["anypoint_data"]["organization_id"] == "oz" for r in out)
        )
        # Name fallback exercised
        self.assertIn("api-321", {r["api_name"] for r in out})

    # Covers: orgs provided as dicts, non-dict in the list is ignored (lines ~92-93)
    def test_orgs_as_dicts_ignores_non_dict_entries(self) -> None:
        client = self._client()
        out = build_inventory(client, orgs=[{"id": "o1", "name": "One"}, "oops"])
        self.assertTrue(
            all(r["metadata"]["anypoint_data"]["organization_id"] == "o1" for r in out)
        )

    # Covers: policy exception branches for both API and environment policies (lines ~349-350, 365)
    def test_policy_calls_raise_are_logged_and_skipped(self) -> None:
        client = self._client()
        client.policies = _RaisingPolicies({}, {})
        opts = InventoryOptions(
            include_api_policies=True, include_environment_policies=True
        )
        out = build_inventory(
            client, options=opts, filters=InventoryFilters(api_names=["api-1"])
        )
        self.assertEqual(out[0]["policy_configurations"], [])

    # Covers: group contracts exception branch (line ~415)
    def test_group_contracts_raise_are_skipped(self) -> None:
        client = self._client()
        client.groups = _FakeGroups({"o1:e1:101": 368690})
        client.contracts = _RaisingGroupContracts({}, {})
        out = build_inventory(client, filters=InventoryFilters(api_names=["api-1"]))
        # We still have API-level contracts from base fakes, but no group contracts added
        apps = out[0]["metadata"]["anypoint_data"]["client_applications"]
        self.assertTrue(all(a.get("contract_type") != "group" for a in apps))

    # Covers: group tier branch where limitsByApi exists but first item is not a dict (lines ~519-520, 523)
    def test_group_tiers_first_item_not_dict_leaves_metrics_none(self) -> None:
        client = self._client()
        client.groups = _FakeGroups({"o1:e1:101": 368690})
        client.tiers = _FunnyGroupTiers({}, {})
        out = build_inventory(client, filters=InventoryFilters(api_names=["api-1"]))
        tiers = [
            t
            for t in out[0]["metadata"]["anypoint_data"]["sla_tiers"]
            if t["scope"] == "group" and t["name"] == "odd-first"
        ]
        self.assertEqual(len(tiers), 1)
        self.assertIsNone(tiers[0]["max_requests"])
        self.assertIsNone(tiers[0]["time_period_seconds"])

    # Covers: options toggles and path building branches late in the function (lines ~559, 586, 593->595)
    def test_paths_and_no_policy_when_disabled(self) -> None:
        client = self._client()
        opts = InventoryOptions(
            base_path=".",
            include_api_policies=False,
            include_environment_policies=False,
        )
        out = build_inventory(
            client, options=opts, filters=InventoryFilters(api_names=["api-1"])
        )
        rec = out[0]
        # Paths present
        self.assertIn("/api-1/v1/api-1.yaml", rec["plugin_config_file_path"])
        self.assertIn("/api-1/v1/api-1.yaml", rec["metadata_file_path"])
        # Policies omitted
        self.assertEqual(rec["policy_configurations"], [])


# ---------- extra fakes to drive specific lines ----------
class _OrgListRaises(_FakeOrganizations):
    def list_accessible(self):
        raise RuntimeError("boom")


class _WeirdGroupTiers(_FakeTiers):
    # defaultLimits None, limitsByApi empty list to hit isinstance(lbs, list) and lbs == False
    def list_group_tiers(self, org_id: str, env_id: str, group_id: int | str):
        return [
            {
                "id": 777,
                "name": "empty-lba",
                "status": "ACTIVE",
                "autoApprove": True,
                "applicationCount": 0,
                "defaultLimits": None,
                "limitsByApi": [],  # exercises 523 path where list truthiness check fails
            }
        ]


class _EndpointDeploymentFallbackApis(_FakeApis):
    def get_instance(self, org_id: str, env_id: str, api_id: int | str):
        # No deployment.type, endpoint.deploymentType present, and runtimeMetadata present, targetMetadata missing
        base = dict(self._details[str(api_id)])
        base["endpoint"] = {
            "uri": "https://example.org",
            "proxyUri": None,
            "deploymentType": "CH2",  # exercises fallback for deployment_type
            "isCloudHub": False,
            "muleVersion4OrAbove": True,
            "runtimeMetadata": {
                "javaVersion": "17"
            },  # exercises java_version endpoint side
        }
        base["deployment"] = (
            {}
        )  # ensures pick favours endpoint and targetMetadata path handled
        return base


class _OnlyBadEnvs(_FakeEnvironments):
    def list_by_orgs(
        self, orgs, *, use_cache: bool = True, skip_unauthorised: bool = True
    ):
        # mixture of bad shapes, only last one valid
        return {
            "o1": [123, {"name": "No Id"}, {"id": "e1", "name": "Sandbox"}],
        }


class _OnlyIdsApis(_FakeApis):
    """No names in instance list to hit api-{id} fallback, but valid detail."""

    def list_instances(self, org_id: str, env_id: str, *, limit: int = 200):
        return [{"id": 321}]

    def get_instance(self, org_id: str, env_id: str, api_id: int | str):
        return {
            "assetId": "",
            "productVersion": "v0",
            "endpoint": {},
            "deployment": {},
            "audit": {},
        }


# ---------- tests hitting exact uncovered areas ----------
class InventoryCollectorEvenMoreFinalBranches(InventoryCollectorTests):

    # 84-86, 89->91, 92-93: orgs given as IDs, discovery raises, fallback stub dicts used
    def test_orgs_ids_discovery_raises_uses_fallback_stub(self) -> None:
        client = self._client()
        client.organizations = _OrgListRaises({})
        # Provide envs for unknown org to allow traversal
        envs = {"oz": [{"id": "ez", "name": "Edge"}]}
        client.apis = _OnlyIdsApis({}, {})
        out = build_inventory(
            client,
            orgs=["oz"],  # triggers ids path
            envs_by_org=envs,  # pruned and used
            filters=InventoryFilters(),  # ignored when orgs explicit
        )
        self.assertTrue(
            all(r["metadata"]["anypoint_data"]["organization_id"] == "oz" for r in out)
        )
        self.assertIn("api-321", {r["api_name"] for r in out})

    # 172, 199: orgs provided as empty list, early return after empty org_name map
    def test_explicit_empty_orgs_returns_empty(self) -> None:
        client = self._client()
        out = build_inventory(client, orgs=[])
        self.assertEqual(out, [])

    # 349-350, 365: both policy fetches raise while flags enabled, nothing appended
    def test_both_policy_calls_raise_are_skipped(self) -> None:
        class _BothRaise(_FakePolicies):
            def list_api_policies(self, *a, **k):
                raise RuntimeError("api pol fail")

            def list_environment_automated_policies(self, *a, **k):
                raise RuntimeError("env pol fail")

        client = self._client()
        client.policies = _BothRaise({}, {})
        opts = InventoryOptions(
            include_api_policies=True, include_environment_policies=True
        )
        out = build_inventory(
            client, options=opts, filters=InventoryFilters(api_names=["api-1"])
        )
        self.assertEqual(out[0]["policy_configurations"], [])

    # 415: group contracts raise branch
    def test_group_contracts_raise_branch(self) -> None:
        class _GrpRaise(_FakeContracts):
            def list_group_contracts(self, *a, **k):
                raise RuntimeError("gc down")

        client = self._client()
        client.groups = _FakeGroups({"o1:e1:101": 368690})
        client.contracts = _GrpRaise({}, {})
        out = build_inventory(client, filters=InventoryFilters(api_names=["api-1"]))
        apps = out[0]["metadata"]["anypoint_data"]["client_applications"]
        self.assertTrue(all(a.get("contract_type") != "group" for a in apps))

    # 523: group tiers path where limitsByApi is [] and defaultLimits is None
    def test_group_tiers_limitsbyapi_empty_list(self) -> None:
        client = self._client()
        client.groups = _FakeGroups({"o1:e1:101": 368690})
        client.tiers = _WeirdGroupTiers({}, {})
        out = build_inventory(client, filters=InventoryFilters(api_names=["api-1"]))
        tiers = [
            t
            for t in out[0]["metadata"]["anypoint_data"]["sla_tiers"]
            if t["scope"] == "group" and t["name"] == "empty-lba"
        ]
        self.assertEqual(len(tiers), 1)
        self.assertIsNone(tiers[0]["max_requests"])
        self.assertIsNone(tiers[0]["time_period_seconds"])

    # 559, 586: deployment_type and java_version fallbacks sourced from endpoint when deployment fields absent
    def test_deployment_and_java_version_endpoint_fallbacks(self) -> None:
        client = self._client()
        client.apis = _EndpointDeploymentFallbackApis(self.instances, self.details)
        out = build_inventory(client, filters=InventoryFilters(api_names=["api-1"]))
        anyp = out[0]["metadata"]["anypoint_data"]
        self.assertEqual(anyp["deployment_type"], "CH2")
        self.assertEqual(anyp["java_version"], "17")

    # 199 and env filtering robustness, with bad env entries skipped
    def test_envs_by_org_mixed_shapes_skip_bad_envs(self) -> None:
        client = self._client()
        client.environments = _OnlyBadEnvs({})
        out = build_inventory(client, orgs=[{"id": "o1", "name": "One"}])
        self.assertTrue(
            all(r["metadata"]["anypoint_data"]["environment_id"] == "e1" for r in out)
        )


class InventoryCollectorRemainingBranches(InventoryCollectorTests):
    # 84-86: org_ids filter excludes all discovered orgs
    def test_filter_org_ids_excludes_all(self) -> None:
        client = self._client()
        out = build_inventory(client, filters=InventoryFilters(org_ids=["no-such-org"]))
        self.assertEqual(out, [])

    # 89->91: org_names filter excludes by name mismatch
    def test_filter_org_names_excludes_by_name(self) -> None:
        client = self._client()
        out = build_inventory(
            client, filters=InventoryFilters(org_names=["not-a-match"])
        )
        # All discovered orgs filtered out
        self.assertEqual(out, [])

    # 92-93: org regex excludes names
    def test_filter_org_regex_excludes(self) -> None:
        client = self._client()
        out = build_inventory(client, filters=InventoryFilters(org_name_regex=r"^ZZZ$"))
        self.assertEqual(out, [])

    # 172: _collect_policy_rows_api skips non-dict items
    def test_collect_policy_rows_api_non_dict_item(self) -> None:
        rows = _collect_policy_rows_api({"policies": [123]})
        self.assertEqual(rows, [])

    # 199: _collect_policy_rows_api skips empty dict row with no meaningful fields
    def test_collect_policy_rows_api_empty_row(self) -> None:
        rows = _collect_policy_rows_api({"policies": [{}]})
        self.assertEqual(rows, [])

    # 349-350: environments list_by_orgs raises, caught and replaced with {}
    def test_envs_list_raises_caught(self) -> None:
        client = self._client()
        client.environments = _RaisingEnvs({})
        # Provide explicit orgs so selection does not rely on discovery
        out = build_inventory(client, orgs=[{"id": "o1", "name": "One"}])
        self.assertEqual(out, [])  # no envs, nothing to traverse

    # 365: applications list returns non-dict, skipped
    def test_applications_non_dict_entry_skipped(self) -> None:
        client = self._client()
        client.applications = _SomeNonDictApplications({})
        # Still should produce inventory, but without credential enrichment
        out = build_inventory(client, filters=InventoryFilters(api_names=["api-1"]))
        apps = out[0]["metadata"]["anypoint_data"]["client_applications"]
        self.assertTrue(all(a.get("client_id") is None for a in apps))

    # 415: instance with id=None is skipped
    def test_instance_missing_id_is_skipped(self) -> None:
        client = self._client()
        client.apis = _InstancesMissingIdApis({}, {})
        out = build_inventory(
            client,
            orgs=[{"id": "o1", "name": "One"}],
            envs_by_org={"o1": [{"id": "e1", "name": "Sandbox"}]},
        )
        # We still get the second valid instance
        self.assertTrue(
            any(r["metadata"]["anypoint_data"]["api_id"] == "999" for r in out)
        )

    # 523: group contracts list contains non-dict, skipped
    def test_group_contracts_non_dict_skipped(self) -> None:
        client = self._client()
        client.groups = _FakeGroups({"o1:e1:101": 368690})
        client.contracts = _GroupContractsNonDict({}, {})
        out = build_inventory(client, filters=InventoryFilters(api_names=["api-1"]))
        apps = out[0]["metadata"]["anypoint_data"]["client_applications"]
        self.assertTrue(all(a.get("contract_type") != "group" for a in apps))

    # 559: API tiers contains non-dict, skipped
    def test_api_tiers_non_dict_skipped(self) -> None:
        client = self._client()
        client.tiers = _ApiTiersNonDict({}, {})
        out = build_inventory(client, filters=InventoryFilters(api_names=["api-1"]))
        tiers = out[0]["metadata"]["anypoint_data"]["sla_tiers"]
        # Only group tiers should remain from base fixtures
        self.assertTrue(all(t["scope"] == "group" for t in tiers))

    # 586: Group tiers contains non-dict, skipped
    def test_group_tiers_non_dict_skipped(self) -> None:
        client = self._client()
        client.groups = _FakeGroups({"o1:e1:101": 368690})
        client.tiers = _GroupTiersNonDict({}, {})
        out = build_inventory(client, filters=InventoryFilters(api_names=["api-1"]))
        tiers = out[0]["metadata"]["anypoint_data"]["sla_tiers"]
        # Only api tiers should be present
        self.assertTrue(all(t["scope"] == "api" for t in tiers))


class InventoryCollectorOrgIncludeBranches(unittest.TestCase):
    def test_org_included_when_id_matches(self) -> None:
        org = {"id": "o1", "name": "One"}
        filt = InventoryFilters(org_ids=["o1"])
        self.assertTrue(_org_included(org, filt, None))

    def test_org_included_when_name_matches_list(self) -> None:
        org = {"id": "o1", "name": "One"}
        filt = InventoryFilters(org_names=["One"])
        self.assertTrue(_org_included(org, filt, None))

    def test_org_included_when_regex_matches(self) -> None:
        org = {"id": "o1", "name": "One"}
        filt = InventoryFilters(org_name_regex=r"^O.*")
        rx = re.compile(filt.org_name_regex)  # compile the regex you passed
        self.assertTrue(_org_included(org, filt, rx))


if __name__ == "__main__":
    unittest.main()
