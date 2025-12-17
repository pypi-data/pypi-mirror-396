from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, Iterable, List, Optional

from .._http import HttpClient, HttpError
from .._logging import LoggerLike, default_logger


@dataclass(frozen=True)
class ExchangeAsset:
    groupId: str
    assetId: str
    version: str
    name: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None
    classifier: Optional[str] = None
    status: Optional[str] = None


def _to_exchange_asset(obj: Dict[str, Any]) -> ExchangeAsset:
    return ExchangeAsset(
        groupId=str(obj.get("groupId", "")),
        assetId=str(obj.get("assetId", "")),
        version=str(obj.get("version", "")),
        name=obj.get("name"),
        description=obj.get("description"),
        type=obj.get("type"),
        classifier=obj.get("classifier"),
        status=obj.get("status"),
    )


def _dedupe(assets: Iterable[ExchangeAsset]) -> List[ExchangeAsset]:
    seen: set[tuple[str, str, str]] = set()
    out: List[ExchangeAsset] = []
    for asset in assets:
        key = (asset.groupId, asset.assetId, asset.version)
        if key and key not in seen:
            seen.add(key)
            out.append(asset)
    return out


class Exchange:
    """
    Anypoint Exchange API for managing assets and specifications.
    """

    def __init__(
        self, http: HttpClient, *, logger: Optional[LoggerLike] = None
    ) -> None:
        self._http = http
        self._log = logger or default_logger().child("resources.exchange")

    def list_assets(
        self,
        *,
        org_id: Optional[str] = None,
        search: Optional[str] = None,
        type_filter: Optional[str] = None,
        offset: int = 0,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        List assets in Exchange.
        """

        params: Dict[str, Any] = {
            "offset": offset,
            "limit": limit,
        }

        if org_id is not None:
            params["organizationIds"] = [org_id]

        if search is not None:
            params["search"] = search
        if type_filter is not None:
            params["type"] = type_filter

        r = self._http.get("/exchange/api/v2/assets", params=params)
        payload = r.json() or []

        self._log.debug("Raw Exchange API response: %s", str(payload)[:200])

        raw = payload if isinstance(payload, list) else []

        items: List[ExchangeAsset] = []
        for obj in raw:
            if isinstance(obj, dict):
                items.append(_to_exchange_asset(obj))

        flat = [asdict(x) for x in _dedupe(items)]
        self._log.debug("Listed %d Exchange assets", len(flat))
        return flat

    def create_asset(
        self,
        org_id: str,
        asset_id: str,
        name: str,
        version: str,
        *,
        description: Optional[str] = None,
        asset_type: str = "rest-api",
        group_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create/publish a new asset in Exchange.
        """
        if group_id is None:
            group_id = org_id

        form_data = {
            "name": name,
            "type": asset_type,
        }

        if description is not None:
            form_data["description"] = description

        self._log.debug("Creating Exchange asset with form_data: %s", form_data)

        r = self._http.post_form(
            f"/exchange/api/v2/organizations/{org_id}/assets/{group_id}/{asset_id}/{version}",
            form_data=form_data,
        )

        self._log.debug(
            "Exchange API response status: %d, body: %s",
            r.status,
            r.text[:500],  # First 500 chars to avoid huge logs
        )

        result = r.json() or {}

        self._log.info(
            "Created Exchange asset '%s' version=%s in org=%s, result keys: %s",
            asset_id,
            version,
            org_id,
            list(result.keys()) if result else "no result",
        )

        return result

    def delete_asset(
        self,
        org_id: str,
        group_id: str,
        asset_id: str,
        version: str,
        *,
        delete_type: str = "hard-delete",
    ) -> None:
        """
        Delete an asset from Exchange.

        Args:
            org_id: Organization ID
            group_id: Group ID of the asset
            asset_id: Asset identifier
            version: Asset version to delete
            delete_type: Type of delete operation ("hard-delete" or "soft-delete")
                        Defaults to "hard-delete" which matches the official CLI behavior
        """
        headers = {
            "X-Delete-Type": delete_type,
        }

        path = f"/exchange/api/v1/organizations/{org_id}/assets/{group_id}/{asset_id}/{version}"

        self._http._request("DELETE", path, headers=headers)

        self._log.info(
            "Deleted Exchange asset %s/%s/%s from org=%s (delete_type=%s)",
            group_id,
            asset_id,
            version,
            org_id,
            delete_type,
        )

    def check_publication_status(self, status_link: str) -> Dict[str, Any]:
        """Check the publication status of an asset using the status link."""
        # Extract just the path from the full URL
        if status_link.startswith("https://anypoint.mulesoft.com"):
            path = status_link.replace("https://anypoint.mulesoft.com", "")
        else:
            path = status_link

        r = self._http.get(path)
        result = r.json() or {}

        self._log.debug("Publication status: %s", result)
        return result

    def list_assets_for_org(
        self,
        org_id: str,
        *,
        search: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        List assets for a specific organization by filtering REST API results.
        """
        all_assets = self.list_assets(limit=250)

        org_assets = [asset for asset in all_assets if asset.get("groupId") == org_id]

        if search:
            search_lower = search.lower()
            org_assets = [
                asset
                for asset in org_assets
                if (
                    asset.get("name", "").lower().find(search_lower) >= 0
                    or asset.get("assetId", "").lower().find(search_lower) >= 0
                )
            ]

        return org_assets[:limit]

    def list_policy_assets(
        self,
        *,
        org_id: Optional[str] = None,
        include_mulesoft_policies: bool = True,
        limit: int = 250,
    ) -> List[Dict[str, Any]]:
        """
        List policy assets from Exchange.

        The Exchange API doesn't support direct filtering by type=policy, so this
        method uses a search-based approach and filters results client-side.

        Args:
            org_id: Optional organization ID to filter by. If provided with
                   include_mulesoft_policies=False, returns only org-specific policies.
            include_mulesoft_policies: Whether to include MuleSoft's standard policies
                                      (from group 68ef9520-24e9-4cf2-b2f5-620025690913).
                                      Default True.
            limit: Maximum number of results to return. Default/max 250 (API limit).

        Returns:
            List of policy definition assets (type="policy").
            Does NOT include policy implementations (type="policy-implementation").
        """
        params: Dict[str, Any] = {
            "search": "policy",
            "limit": limit,
        }

        # If org_id provided without including MuleSoft policies, use organizationId filter
        if org_id and not include_mulesoft_policies:
            params = {
                "organizationId": org_id,
                "limit": limit,
            }

        r = self._http.get("/exchange/api/v2/assets", params=params)
        assets = r.json() or []

        # Filter for policy type only (not policy-implementation)
        policies = [
            asset
            for asset in assets
            if isinstance(asset, dict) and asset.get("type") == "policy"
        ]

        # If org_id specified with include_mulesoft_policies=True, filter to show
        # both org policies and MuleSoft standard policies
        mulesoft_group_id = "68ef9520-24e9-4cf2-b2f5-620025690913"
        if org_id and include_mulesoft_policies:
            policies = [
                p for p in policies if p.get("groupId") in (org_id, mulesoft_group_id)
            ]

        self._log.debug("Found %d policy assets", len(policies))
        return policies

    def list_policy_implementations(
        self,
        *,
        org_id: Optional[str] = None,
        include_mulesoft_policies: bool = True,
        limit: int = 250,
    ) -> List[Dict[str, Any]]:
        """
        List policy implementation assets from Exchange.

        Args:
            org_id: Optional organization ID to filter by.
            include_mulesoft_policies: Whether to include MuleSoft's standard
                                      policy implementations. Default True.
            limit: Maximum number of results to return. Default/max 250 (API limit).

        Returns:
            List of policy implementation assets (type="policy-implementation").
        """
        params: Dict[str, Any] = {
            "search": "policy",
            "limit": limit,
        }

        if org_id and not include_mulesoft_policies:
            params = {
                "organizationId": org_id,
                "limit": limit,
            }

        r = self._http.get("/exchange/api/v2/assets", params=params)
        assets = r.json() or []

        # Filter for policy-implementation type
        implementations = [
            asset
            for asset in assets
            if isinstance(asset, dict) and asset.get("type") == "policy-implementation"
        ]

        mulesoft_group_id = "68ef9520-24e9-4cf2-b2f5-620025690913"
        if org_id and include_mulesoft_policies:
            implementations = [
                p
                for p in implementations
                if p.get("groupId") in (org_id, mulesoft_group_id)
            ]

        self._log.debug("Found %d policy implementation assets", len(implementations))
        return implementations

    def get_asset(
        self,
        group_id: str,
        asset_id: str,
        version: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get details of a specific Exchange asset.

        Args:
            group_id: Group ID of the asset (typically org_id for custom assets)
            asset_id: Asset identifier
            version: Optional specific version. If not provided, returns latest version info.

        Returns:
            Dict containing the asset details including files, metadata, etc.

        Raises:
            HttpError: If the asset is not found (404) or other errors
        """
        if version:
            path = f"/exchange/api/v2/assets/{group_id}/{asset_id}/{version}"
        else:
            path = f"/exchange/api/v2/assets/{group_id}/{asset_id}"

        r = self._http.get(path)
        result = r.json() or {}

        self._log.debug(
            "Retrieved Exchange asset %s/%s%s",
            group_id,
            asset_id,
            f"/{version}" if version else "",
        )

        return result

    def list_resources(
        self,
        group_id: str,
        asset_id: str,
        version: str,
        *,
        draft: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        List resources for an Exchange asset (published or draft).

        Args:
            group_id: Group ID of the asset
            asset_id: Asset identifier
            version: Asset version
            draft: If True, list draft resources; if False, list published resources
        """
        # Build URL - from uris.js patterns
        if draft:
            path = f"/exchange/api/v2/assets/{group_id}/{asset_id}/{version}/portal/draft/resources"
        else:
            path = f"/exchange/api/v2/assets/{group_id}/{asset_id}/{version}/portal/resources"

        r = self._http.get(path)
        resources = r.json() or []

        # Extract resource paths like the official CLI does
        resource_paths = []
        if isinstance(resources, list):
            for resource in resources:
                if isinstance(resource, dict) and "path" in resource:
                    resource_paths.append(resource)

        status = "draft" if draft else "published"
        self._log.debug(
            "Found %d %s resources for asset %s/%s/%s",
            len(resource_paths),
            status,
            group_id,
            asset_id,
            version,
        )

        return resource_paths

    def upload_resource(
        self,
        group_id: str,
        asset_id: str,
        version: str,
        file_path: str,
        *,
        resource_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Upload a resource (like RAML spec) to an Exchange asset as draft.

        Args:
            group_id: Group ID of the asset
            asset_id: Asset identifier
            version: Asset version
            file_path: Path to the file to upload
            resource_name: Optional name for the resource (defaults to filename)
        """
        import os

        if resource_name is None:
            resource_name = os.path.basename(file_path)

        # URL pattern from uris.js resourceUpload function
        path = f"/exchange/api/v2/assets/{group_id}/{asset_id}/{version}/portal/draft/resources"

        # Read file content
        with open(file_path, "rb") as f:
            file_content = f.read()

        # Prepare form data for multipart upload
        # The file field name might need to be 'file' or 'resource' - check API docs
        form_data = {"file": (resource_name, file_content, "application/octet-stream")}

        # Use the existing post_form method which handles multipart properly
        r = self._http.post_form_ext(path, form_data)

        result = r.json() or {}

        self._log.info(
            "Uploaded resource %s to asset %s/%s/%s",
            resource_name,
            group_id,
            asset_id,
            version,
        )

        return result

    def delete_resource(
        self,
        group_id: str,
        asset_id: str,
        version: str,
        resource_path: str,
    ) -> None:
        """
        Delete a resource from an Exchange asset (from draft).

        Args:
            group_id: Group ID of the asset
            asset_id: Asset identifier
            version: Asset version
            resource_path: Path of the resource to delete
        """
        # URL pattern from uris.js deleteAssetResource function
        path = f"/exchange/api/v2/assets/{group_id}/{asset_id}/{version}/portal/draft/{resource_path}"

        self._http._request("DELETE", path)

        self._log.info(
            "Deleted resource %s from asset %s/%s/%s",
            resource_path,
            group_id,
            asset_id,
            version,
        )

    def download_resource(
        self,
        group_id: str,
        asset_id: str,
        version: str,
        resource_path: str,
        output_path: str,
        *,
        draft: bool = False,
    ) -> None:
        """
        Download a resource from an Exchange asset.

        Args:
            group_id: Group ID of the asset
            asset_id: Asset identifier
            version: Asset version
            resource_path: Path of the resource to download
            output_path: Local path where to save the file
            draft: If True, download from draft; if False, from published
        """
        # URL pattern from uris.js
        if draft:
            path = f"/exchange/api/v2/assets/{group_id}/{asset_id}/{version}/portal/draft/{resource_path}"
        else:
            path = f"/exchange/api/v2/assets/{group_id}/{asset_id}/{version}/portal/{resource_path}"

        r = self._http.get(path)

        # Save the file
        with open(output_path, "wb") as f:
            f.write(r.text.encode() if isinstance(r.text, str) else r._resp.content)

        status = "draft" if draft else "published"
        self._log.info(
            "Downloaded %s resource %s from asset %s/%s/%s to %s",
            status,
            resource_path,
            group_id,
            asset_id,
            version,
            output_path,
        )

    def create_asset_with_raml_bundle(
        self,
        org_id: str,
        group_id: str,
        asset_id: str,
        version: str,
        raml_zip_path: str,
        *,
        name: str,
        description: Optional[str] = None,
        main_file: str = "api.raml",
        api_version: str = "v1",
        sync_publication: bool = True,
    ) -> Dict[str, Any]:
        """
        Create and publish an Exchange asset with a RAML specification bundle.

        This method uses the working Exchange API pattern that directly uploads
        a ZIP file containing RAML specifications during asset creation.

        Args:
            org_id: Organization ID
            group_id: Group ID (typically same as org_id)
            asset_id: Unique identifier for the asset
            version: Asset version (e.g., "1.0.0")
            raml_zip_path: Path to ZIP file containing RAML specifications
            name: Display name for the asset
            description: Optional description of the asset
            main_file: Main RAML file name inside the ZIP (default: "api.raml")
            api_version: API version identifier (default: "v1")
            sync_publication: Whether to wait for publication to complete (default: True)

        Returns:
            Dict containing the creation response from Exchange API

        Raises:
            HttpError: If the asset creation fails (including 409 conflicts)
            FileNotFoundError: If the raml_zip_path doesn't exist
        """
        import os

        # Validate the ZIP file exists
        if not os.path.exists(raml_zip_path):
            raise FileNotFoundError(f"RAML ZIP file not found: {raml_zip_path}")

        # Read the ZIP file content
        with open(raml_zip_path, "rb") as zip_file:
            file_content = zip_file.read()

        # Prepare form data using the working Exchange API pattern
        # Use the exact same structure as your working cgpt_test.py script
        form_data = {
            "name": name,
            "description": description or f"RAML API specification for {name}",
            "properties.mainFile": main_file,
            "properties.apiVersion": api_version,
            "status": "published",
            # Add the ZIP file using the pattern that works
            "files.raml.zip": (
                os.path.basename(raml_zip_path),
                file_content,
                "application/zip",
            ),
        }

        # Headers for synchronous publication
        headers = {}
        if sync_publication:
            headers["x-sync-publication"] = "true"

        # Use the exact working API endpoint
        path = f"/exchange/api/v2/organizations/{org_id}/assets/{group_id}/{asset_id}/{version}"

        self._log.debug(
            "Creating Exchange asset with RAML bundle: %s/%s/%s",
            group_id,
            asset_id,
            version,
        )

        # Use post_form_ext which handles multipart form data correctly
        # Note: post_form_ext raises HttpError for non-2xx responses (including 409)
        try:
            response = self._http.post_form_ext(path, form_data, headers)

            # Parse the response
            result = response.json() if response.text else {}

            self._log.info(
                "Successfully created Exchange asset with RAML bundle: %s/%s/%s",
                group_id,
                asset_id,
                version,
            )

            return result

        except HttpError:
            raise
        except Exception as e:
            # Convert other exceptions (e.g., file I/O errors) to HttpError
            raise HttpError(
                status=0, message=f"Error creating asset: {str(e)}", body=None
            ) from e

    def create_raml_zip_bundle(
        self,
        raml_content: str,
        main_file: str = "api.raml",
        additional_files: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        Create a ZIP bundle containing RAML specifications.

        Args:
            raml_content: The main RAML specification content
            main_file: Name for the main RAML file (default: "api.raml")
            additional_files: Optional dict of {filename: content} for additional files

        Returns:
            Path to the created ZIP file (in temp directory)

        Note:
            Caller is responsible for cleaning up the returned ZIP file.
        """
        import os
        import tempfile
        import zipfile

        # Create temporary directory and ZIP file
        tmpdir = tempfile.mkdtemp(prefix="raml_bundle_")
        zip_path = os.path.join(tmpdir, "raml-bundle.zip")

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            # Add main RAML file
            zipf.writestr(main_file, raml_content)

            # Add any additional files
            if additional_files:
                for filename, content in additional_files.items():
                    zipf.writestr(filename, content)

        return zip_path

    def create_policy_definition(
        self,
        org_id: str,
        asset_id: str,
        version: str,
        name: str,
        schema_json: str,
        metadata_yaml: str,
        *,
        group_id: Optional[str] = None,
        sync_publication: bool = False,
    ) -> Dict[str, Any]:
        """
        Create and publish a custom policy definition asset in Exchange.

        A policy definition describes the policy's configuration schema and metadata.
        After creating a definition, you must also create a policy implementation
        using create_policy_implementation().

        Args:
            org_id: Organization ID
            asset_id: Unique identifier for the policy asset (e.g., "my-custom-policy")
            version: Asset version (e.g., "1.0.0")
            name: Display name for the policy
            schema_json: JSON Schema content defining policy configuration parameters
            metadata_yaml: YAML content with policy definition (must start with
                          "#%Policy Definition 0.1")
            group_id: Group ID (defaults to org_id)
            sync_publication: Whether to wait for publication to complete (default False)

        Returns:
            Dict containing the creation response, typically with a
            'publicationStatusLink' for async status checking.

        Raises:
            HttpError: If the asset creation fails (including 409 conflicts)

        Example metadata_yaml:
            #%Policy Definition 0.1
            name: my_custom_policy
            description: My custom policy description
            category: Custom
            violationCategory: authentication
            resourceLevelSupported: true
            encryptionSupported: false
            standalone: false
            requiredCharacteristics: []
            providedCharacteristics: []
            configuration: []
        """
        if group_id is None:
            group_id = org_id

        # Prepare multipart form data
        # The schema file uses "schema" classifier (not "definition.schema")
        # as seen in working policy assets: classifier="schema", packaging="json"
        form_data = {
            "name": name,
            "type": "policy",
            "status": "published",
            "files.schema.json": (
                f"{asset_id}-schema.json",
                schema_json.encode("utf-8"),
                "application/json",
            ),
            "files.metadata.yaml": (
                f"{asset_id}.yaml",
                metadata_yaml.encode("utf-8"),
                "application/x-yaml",
            ),
        }

        headers = {}
        if sync_publication:
            headers["x-sync-publication"] = "true"
        else:
            headers["x-sync-publication"] = "false"

        path = f"/exchange/api/v2/organizations/{org_id}/assets/{group_id}/{asset_id}/{version}"

        self._log.debug(
            "Creating policy definition asset: %s/%s/%s",
            group_id,
            asset_id,
            version,
        )

        response = self._http.post_form_ext(path, form_data, headers)
        result = response.json() if response.text else {}

        self._log.info(
            "Created policy definition '%s' version=%s in org=%s",
            asset_id,
            version,
            org_id,
        )

        return result

    def create_policy_implementation(
        self,
        org_id: str,
        asset_id: str,
        version: str,
        name: str,
        policy_jar_path: str,
        implementation_yaml: str,
        policy_definition_gav: str,
        *,
        group_id: Optional[str] = None,
        sync_publication: bool = False,
    ) -> Dict[str, Any]:
        """
        Create and publish a custom policy implementation asset in Exchange.

        A policy implementation contains the compiled JAR and links to a policy
        definition. This should be called after create_policy_definition().

        Args:
            org_id: Organization ID
            asset_id: Unique identifier for the implementation asset
                     (typically "{policy_asset_id}-imp")
            version: Asset version (e.g., "1.0.0")
            name: Display name (typically same as policy definition name)
            policy_jar_path: Path to the compiled policy JAR file
            implementation_yaml: YAML content with implementation metadata
                                (must start with "#%Policy Implementation 1.0")
            policy_definition_gav: GAV coordinates of the policy definition
                                  in format "groupId:assetId:version"
            group_id: Group ID (defaults to org_id)
            sync_publication: Whether to wait for publication to complete (default False)

        Returns:
            Dict containing the creation response, typically with a
            'publicationStatusLink' for async status checking.

        Raises:
            HttpError: If the asset creation fails
            FileNotFoundError: If the policy_jar_path doesn't exist

        Example implementation_yaml:
            #%Policy Implementation 1.0
            technology: mule4
            minRuntimeVersion: 4.6.8
            supportedJavaVersions:
              - "8"
              - "11"
              - "17"
        """
        import os

        if group_id is None:
            group_id = org_id

        # Validate JAR file exists
        if not os.path.exists(policy_jar_path):
            raise FileNotFoundError(f"Policy JAR file not found: {policy_jar_path}")

        # Read JAR file content
        with open(policy_jar_path, "rb") as jar_file:
            jar_content = jar_file.read()

        jar_filename = os.path.basename(policy_jar_path)

        # Prepare multipart form data
        form_data = {
            "name": name,
            "type": "policy-implementation",
            "status": "published",
            "dependencies": policy_definition_gav,
            "files.binary.jar": (
                jar_filename,
                jar_content,
                "application/java-archive",
            ),
            "files.metadata.yaml": (
                "implementation.yaml",
                implementation_yaml.encode("utf-8"),
                "application/x-yaml",
            ),
        }

        headers = {}
        if sync_publication:
            headers["x-sync-publication"] = "true"
        else:
            headers["x-sync-publication"] = "false"

        path = f"/exchange/api/v2/organizations/{org_id}/assets/{group_id}/{asset_id}/{version}"

        self._log.debug(
            "Creating policy implementation asset: %s/%s/%s (depends on %s)",
            group_id,
            asset_id,
            version,
            policy_definition_gav,
        )

        response = self._http.post_form_ext(path, form_data, headers)
        result = response.json() if response.text else {}

        self._log.info(
            "Created policy implementation '%s' version=%s in org=%s",
            asset_id,
            version,
            org_id,
        )

        return result

    def create_custom_policy(
        self,
        org_id: str,
        policy_asset_id: str,
        version: str,
        name: str,
        description: str,
        schema_json: str,
        policy_jar_path: str,
        *,
        group_id: Optional[str] = None,
        category: str = "Custom",
        violation_category: str = "authentication",
        resource_level_supported: bool = True,
        technology: str = "mule4",
        min_runtime_version: str = "4.6.8",
        supported_java_versions: Optional[List[str]] = None,
        sync_publication: bool = False,
    ) -> Dict[str, Any]:
        """
        Create a complete custom policy (definition + implementation) in Exchange.

        This is a convenience method that creates both the policy definition
        and its implementation in one call.

        Args:
            org_id: Organization ID
            policy_asset_id: Unique identifier for the policy (e.g., "my-custom-policy")
            version: Asset version (e.g., "1.0.0")
            name: Display name for the policy
            description: Policy description
            schema_json: JSON Schema content defining policy configuration parameters
            policy_jar_path: Path to the compiled policy JAR file
            group_id: Group ID (defaults to org_id)
            category: Policy category (default: "Custom")
            violation_category: Violation type (default: "authentication")
            resource_level_supported: Whether policy can be applied at resource level
            technology: Implementation technology (default: "mule4")
            min_runtime_version: Minimum Mule runtime version (default: "4.6.8")
            supported_java_versions: List of supported Java versions
                                    (default: ["8", "11", "17"])
            sync_publication: Whether to wait for publication to complete

        Returns:
            Dict with 'definition' and 'implementation' keys containing
            the respective creation responses.

        Raises:
            HttpError: If asset creation fails
            FileNotFoundError: If the policy_jar_path doesn't exist
        """
        if group_id is None:
            group_id = org_id

        if supported_java_versions is None:
            supported_java_versions = ["8", "11", "17"]

        # Generate metadata YAML for policy definition
        metadata_yaml = f"""#%Policy Definition 0.1
name: {name}
description: {description}
category: {category}
violationCategory: {violation_category}
resourceLevelSupported: {str(resource_level_supported).lower()}
encryptionSupported: false
standalone: false
requiredCharacteristics: []
providedCharacteristics: []
configuration: []
"""

        # Generate implementation YAML
        java_versions_yaml = "\n".join(f'  - "{v}"' for v in supported_java_versions)
        implementation_yaml = f"""#%Policy Implementation 1.0
technology: {technology}
minRuntimeVersion: {min_runtime_version}
supportedJavaVersions:
{java_versions_yaml}
"""

        # Create policy definition
        definition_result = self.create_policy_definition(
            org_id=org_id,
            asset_id=policy_asset_id,
            version=version,
            name=name,
            schema_json=schema_json,
            metadata_yaml=metadata_yaml,
            group_id=group_id,
            sync_publication=sync_publication,
        )

        # Create policy implementation (with -imp suffix)
        implementation_asset_id = f"{policy_asset_id}-imp"
        policy_definition_gav = f"{group_id}:{policy_asset_id}:{version}"

        implementation_result = self.create_policy_implementation(
            org_id=org_id,
            asset_id=implementation_asset_id,
            version=version,
            name=name,
            policy_jar_path=policy_jar_path,
            implementation_yaml=implementation_yaml,
            policy_definition_gav=policy_definition_gav,
            group_id=group_id,
            sync_publication=sync_publication,
        )

        return {
            "definition": definition_result,
            "implementation": implementation_result,
        }
