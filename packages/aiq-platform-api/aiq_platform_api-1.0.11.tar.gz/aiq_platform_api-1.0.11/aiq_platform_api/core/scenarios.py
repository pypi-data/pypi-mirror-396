import copy
from typing import Optional, Dict, Any, AsyncGenerator

from aiq_platform_api.core.async_utils import async_islice
from aiq_platform_api.core.client import AttackIQClient
from aiq_platform_api.core.constants import ScenarioTemplateType, SCENARIO_TEMPLATE_IDS
from aiq_platform_api.core.logger import AttackIQLogger
from aiq_platform_api.core.tags import Tags

logger = AttackIQLogger.get_logger(__name__)


class Scenarios:
    """Utilities for interacting with Scenario models.

    API Endpoint: /v1/scenarios
    """

    ENDPOINT = "v1/scenarios"

    @staticmethod
    async def list_scenarios(
        client: AttackIQClient,
        params: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = 10,
        offset: Optional[int] = 0,
        ordering: Optional[str] = "-modified",
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """List scenarios with minimal fields, ordering, and offset support.

        Args:
            ordering: Sort order (default: -modified for most recent first)
                     Use '-' prefix for descending (e.g., '-modified', '-created')
                     Omit '-' for ascending (e.g., 'modified', 'created', 'name')
        """
        request_params = params.copy() if params else {}
        request_params["minimal"] = "true"
        if "ordering" not in request_params and ordering:
            request_params["ordering"] = ordering
        logger.info(f"Listing scenarios with params: {request_params}, limit: {limit}, offset: {offset}")
        generator = client.get_all_objects(Scenarios.ENDPOINT, params=request_params)
        stop = offset + limit if limit is not None else None
        async for scenario in async_islice(generator, offset, stop):
            yield scenario

    @staticmethod
    async def get_scenario(client: AttackIQClient, scenario_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific scenario by its ID."""
        endpoint = f"{Scenarios.ENDPOINT}/{scenario_id}"
        logger.info(f"Getting scenario: {scenario_id}")
        return await client.get_object(endpoint)

    @staticmethod
    async def update_scenario(
        client: AttackIQClient,
        scenario_id: str,
        data: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """Update a scenario by its ID."""
        endpoint = f"{Scenarios.ENDPOINT}/{scenario_id}"
        logger.info(f"Updating scenario {scenario_id} with data: {data}")
        return await client.patch_object(endpoint, data)

    @staticmethod
    async def save_copy(client: AttackIQClient, scenario_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a copy of an existing scenario."""
        endpoint = f"{Scenarios.ENDPOINT}/{scenario_id}/save_copy"
        logger.info(f"Creating copy of scenario {scenario_id} with data: {data}")
        return await client.post_object(endpoint, data=data)

    @staticmethod
    async def delete_scenario(client: AttackIQClient, scenario_id: str) -> bool:
        """Delete a specific scenario by its ID."""
        endpoint = f"{Scenarios.ENDPOINT}/{scenario_id}"
        logger.info(f"Deleting scenario: {scenario_id}")
        response = await client.delete_object(endpoint)
        if response is not None and 200 <= response["status_code"] < 300:
            logger.info(f"Successfully deleted scenario: {scenario_id}")
            return True
        logger.error(f"Failed to delete scenario: {scenario_id}")
        return False

    @staticmethod
    async def search_scenarios(
        client: AttackIQClient,
        query: Optional[str] = None,
        limit: Optional[int] = 20,
        offset: Optional[int] = 0,
        ordering: Optional[str] = "-modified",
    ) -> dict:
        """Search or list scenarios.
        - With query: Search by keyword, MITRE technique ID, or tag
        - Without query: List all scenarios (paginated)
        Returns {"count": total, "results": [...]}

        Args:
            ordering: Sort order (default: -modified for most recent first)
                     Use '-' prefix for descending (e.g., '-modified', '-created')
                     Omit '-' for ascending (e.g., 'modified', 'created', 'name')
        """
        logger.info(
            f"Searching scenarios with query: '{query}', limit: {limit}, offset: {offset}, ordering: {ordering}"
        )
        params = {"minimal": "true", "limit": limit, "offset": offset}
        if query:
            params["search"] = query
        if "ordering" not in params and ordering:
            params["ordering"] = ordering
        url = client._build_url(Scenarios.ENDPOINT, params)
        data = await client._make_request(url, method="get", json=None)
        total_count = data.get("count", 0)
        results = data.get("results", [])
        logger.info(f"Found {total_count} total scenarios matching '{query}', returning {len(results)}")
        return {"count": total_count, "results": results}

    @staticmethod
    async def list_scenarios_by_tag(
        client: AttackIQClient,
        tag_id: str,
        limit: Optional[int] = 20,
        offset: Optional[int] = 0,
        ordering: Optional[str] = "-modified",
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {"minimal": "true", "limit": limit, "offset": offset, "tag": tag_id}
        if ordering:
            params["ordering"] = ordering
        logger.info(f"Listing scenarios by tag {tag_id} with params: {params}")
        url = client._build_url(Scenarios.ENDPOINT, params)
        data = await client._make_request(url, method="get", json=None)
        response = {"count": data["count"], "results": data["results"]}
        if "detail" in data:
            response["detail"] = data["detail"]
        return response

    @staticmethod
    async def search_scenarios_by_tag(
        client: AttackIQClient,
        tag_query: str,
        limit: Optional[int] = 20,
        offset: Optional[int] = 0,
        ordering: Optional[str] = "-modified",
    ) -> Dict[str, Any]:
        query = tag_query
        normalized_detail = None
        if "." in tag_query:
            normalized = tag_query.replace(".", "")
            normalized_detail = f"Normalized MITRE ID {tag_query} -> {normalized} due to platform storage format"
            query = normalized

        logger.info(f"Searching scenarios for tag query '{query}'")
        tag_search = await Tags.search_tags(client, search=query, limit=limit, offset=0)
        tags = tag_search["results"]
        detail = tag_search.get("detail")
        if not detail and normalized_detail:
            detail = normalized_detail

        scenarios = []
        seen_ids = set()
        for tag in tags:
            tag_id = tag["id"]
            tag_scenarios = await Scenarios.list_scenarios_by_tag(
                client, tag_id, limit=limit + offset, offset=0, ordering=ordering
            )
            for scenario in tag_scenarios["results"]:
                sid = scenario["id"]
                if sid not in seen_ids:
                    seen_ids.add(sid)
                    scenarios.append(scenario)

        scenarios = scenarios[offset : offset + limit]

        response = {"count": len(seen_ids), "tags": tags, "scenarios": scenarios}
        if detail:
            response["detail"] = detail
        return response

    @staticmethod
    async def search_scenarios_by_mitre(
        client: AttackIQClient,
        technique_id: str,
        limit: Optional[int] = 20,
        offset: Optional[int] = 0,
        ordering: Optional[str] = "-modified",
    ) -> Dict[str, Any]:
        logger.info(f"search_scenarios_by_mitre is an alias for search_scenarios_by_tag with query '{technique_id}'")
        return await Scenarios.search_scenarios_by_tag(
            client=client,
            tag_query=technique_id,
            limit=limit,
            offset=offset,
            ordering=ordering,
        )

    @staticmethod
    async def get_scenario_details(client: AttackIQClient, scenario_id: str) -> Optional[Dict[str, Any]]:
        """Get complete details for a specific scenario."""
        return await Scenarios.get_scenario(client, scenario_id)

    @staticmethod
    def _validate_download_to_memory_model(model_json: Dict[str, Any]) -> None:
        target_system = model_json.get("target_system")
        sha256_hash = model_json.get("sha256_hash")
        missing_fields = []
        if not target_system:
            missing_fields.append("target_system")
        if not sha256_hash:
            missing_fields.append("sha256_hash")

        allowed_target_systems = {"attack_infrastructure", "url"}
        if target_system and target_system not in allowed_target_systems:
            allowed = ", ".join(sorted(allowed_target_systems))
            raise ValueError(f"Unsupported target_system '{target_system}'. Allowed: {allowed}")

        if target_system == "attack_infrastructure" and not model_json.get("attack_infrastructure_resource"):
            missing_fields.append("attack_infrastructure_resource")
        if target_system == "url" and not model_json.get("download_url"):
            missing_fields.append("download_url")

        if model_json.get("use_auth"):
            if not model_json.get("username") or not model_json.get("password"):
                missing_fields.append("username/password when use_auth is true")

        if missing_fields:
            missing = ", ".join(missing_fields)
            raise ValueError(f"Missing required fields for download-to-memory scenario: {missing}")

    @staticmethod
    def build_download_to_memory_model_json(
        base_model_json: Dict[str, Any],
        *,
        target_system: str,
        sha256_hash: str,
        attack_infrastructure_resource: Optional[str] = None,
        download_url: Optional[str] = None,
        attack_infrastructure_protocol: Optional[str] = None,
        download_method: Optional[str] = None,
        check_if_executable: Optional[bool] = None,
        use_auth: Optional[bool] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        http_proxy_conf: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Build a validated model_json payload for Download File to Memory scenarios.

        This preserves the template defaults from base_model_json while applying overrides.
        """
        model_json = copy.deepcopy(base_model_json) if base_model_json else {}

        model_json["target_system"] = target_system
        model_json["sha256_hash"] = sha256_hash

        if attack_infrastructure_protocol is not None:
            model_json["attack_infrastructure_protocol"] = attack_infrastructure_protocol
        if download_method is not None:
            model_json["download_method"] = download_method
        if check_if_executable is not None:
            model_json["check_if_executable"] = check_if_executable
        if use_auth is not None:
            model_json["use_auth"] = use_auth
        if http_proxy_conf is not None:
            model_json["http_proxy_conf"] = http_proxy_conf

        if attack_infrastructure_resource is not None:
            model_json["attack_infrastructure_resource"] = attack_infrastructure_resource
        if download_url is not None:
            model_json["download_url"] = download_url
        if username is not None:
            model_json["username"] = username
        if password is not None:
            model_json["password"] = password

        Scenarios._validate_download_to_memory_model(model_json)
        return model_json

    @staticmethod
    def _merge_value(provided: Optional[Any], existing: Optional[Any]) -> Optional[Any]:
        return existing if provided is None else provided

    @staticmethod
    def _build_description_payload(summary: Optional[str]) -> Optional[Dict[str, Any]]:
        if not summary:
            return None
        return {
            "description_json": {
                "summary": summary,
                "prerequisites": "",
                "failure_criteria": "",
                "prevention_criteria": "",
                "additional_information": "",
            }
        }

    @staticmethod
    async def create_download_to_memory_scenario(
        client: AttackIQClient,
        name: str,
        *,
        target_system: str,
        sha256_hash: str,
        attack_infrastructure_resource: Optional[str] = None,
        download_url: Optional[str] = None,
        attack_infrastructure_protocol: str = "http",
        download_method: str = "python_requests",
        check_if_executable: bool = False,
        use_auth: bool = False,
        username: Optional[str] = None,
        password: Optional[str] = None,
        http_proxy_conf: str = "no_proxy",
        fork_template: bool = False,
        summary: Optional[str] = None,
        extras: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create a Download File to Memory scenario from its template."""
        template_id = SCENARIO_TEMPLATE_IDS[ScenarioTemplateType.DOWNLOAD_TO_MEMORY]
        logger.info(f"Creating Download File to Memory scenario '{name}' from template {template_id}")
        template = await Scenarios.get_scenario(client, template_id)
        if not template:
            raise ValueError(f"Template scenario not found: {template_id}")

        model_json = Scenarios.build_download_to_memory_model_json(
            base_model_json=template.get("model_json") or {},
            target_system=target_system,
            sha256_hash=sha256_hash,
            attack_infrastructure_resource=attack_infrastructure_resource,
            download_url=download_url,
            attack_infrastructure_protocol=attack_infrastructure_protocol,
            download_method=download_method,
            check_if_executable=check_if_executable,
            use_auth=use_auth,
            username=username,
            password=password,
            http_proxy_conf=http_proxy_conf,
        )

        created = await Scenarios.save_copy(
            client,
            template_id,
            {
                "name": name,
                "model_json": model_json,
                "fork_template": fork_template,
            },
        )
        if not created:
            raise ValueError("Failed to create download-to-memory scenario")

        patch_payload: Dict[str, Any] = {}
        description_payload = Scenarios._build_description_payload(summary)
        if description_payload:
            patch_payload.update(description_payload)
        if extras:
            patch_payload["extras"] = extras
        if patch_payload:
            logger.info(f"Patching created scenario {created['id']} with description/extras")
            await Scenarios.update_scenario(client, created["id"], patch_payload)

        return created

    @staticmethod
    async def update_download_to_memory_scenario(
        client: AttackIQClient,
        scenario_id: str,
        *,
        target_system: Optional[str] = None,
        sha256_hash: Optional[str] = None,
        attack_infrastructure_resource: Optional[str] = None,
        download_url: Optional[str] = None,
        attack_infrastructure_protocol: Optional[str] = None,
        download_method: Optional[str] = None,
        check_if_executable: Optional[bool] = None,
        use_auth: Optional[bool] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        http_proxy_conf: Optional[str] = None,
        summary: Optional[str] = None,
        extras: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Update an existing Download File to Memory scenario."""
        scenario = await Scenarios.get_scenario(client, scenario_id)
        if not scenario:
            raise ValueError(f"Scenario not found: {scenario_id}")

        existing_model = scenario.get("model_json") or {}
        model_json = Scenarios.build_download_to_memory_model_json(
            base_model_json=existing_model,
            target_system=Scenarios._merge_value(target_system, existing_model.get("target_system")),
            sha256_hash=Scenarios._merge_value(sha256_hash, existing_model.get("sha256_hash")),
            attack_infrastructure_resource=Scenarios._merge_value(
                attack_infrastructure_resource, existing_model.get("attack_infrastructure_resource")
            ),
            download_url=Scenarios._merge_value(download_url, existing_model.get("download_url")),
            attack_infrastructure_protocol=Scenarios._merge_value(
                attack_infrastructure_protocol, existing_model.get("attack_infrastructure_protocol")
            ),
            download_method=Scenarios._merge_value(download_method, existing_model.get("download_method")),
            check_if_executable=Scenarios._merge_value(check_if_executable, existing_model.get("check_if_executable")),
            use_auth=Scenarios._merge_value(use_auth, existing_model.get("use_auth")),
            username=Scenarios._merge_value(username, existing_model.get("username")),
            password=Scenarios._merge_value(password, existing_model.get("password")),
            http_proxy_conf=Scenarios._merge_value(http_proxy_conf, existing_model.get("http_proxy_conf")),
        )

        payload: Dict[str, Any] = {"model_json": model_json}
        description_payload = Scenarios._build_description_payload(summary)
        if description_payload:
            payload.update(description_payload)
        if extras:
            payload["extras"] = extras

        if not payload:
            raise ValueError("No updates specified for scenario")

        logger.info(f"Updating Download File to Memory scenario {scenario_id}")
        updated = await Scenarios.update_scenario(client, scenario_id, payload)
        return updated or await Scenarios.get_scenario(client, scenario_id)

    @staticmethod
    def _validate_native_api_model(model_json: Dict[str, Any]) -> None:
        apis = model_json.get("apis")
        if not apis or not isinstance(apis, list):
            raise ValueError("apis list is required for native_api scenarios")
        for idx, api in enumerate(apis):
            if not isinstance(api, dict):
                raise ValueError(f"apis[{idx}] must be an object")
            if not api.get("api"):
                raise ValueError(f"apis[{idx}]['api'] is required")

    @staticmethod
    def build_native_api_model_json(
        base_model_json: Dict[str, Any],
        *,
        apis: list[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Build validated model_json for Native API scenarios."""
        model_json = copy.deepcopy(base_model_json) if base_model_json else {}
        model_json["apis"] = apis
        Scenarios._validate_native_api_model(model_json)
        return model_json

    @staticmethod
    async def create_native_api_scenario(
        client: AttackIQClient,
        name: str,
        *,
        apis: list[Dict[str, Any]],
        fork_template: bool = False,
        summary: Optional[str] = None,
        extras: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        template_id = SCENARIO_TEMPLATE_IDS[ScenarioTemplateType.NATIVE_API]
        logger.info(f"Creating Native API scenario '{name}' from template {template_id}")
        template = await Scenarios.get_scenario(client, template_id)
        if not template:
            raise ValueError(f"Template scenario not found: {template_id}")

        model_json = Scenarios.build_native_api_model_json(
            base_model_json=template.get("model_json") or {},
            apis=apis,
        )

        created = await Scenarios.save_copy(
            client,
            template_id,
            {
                "name": name,
                "model_json": model_json,
                "fork_template": fork_template,
            },
        )
        if not created:
            raise ValueError("Failed to create native_api scenario")

        patch_payload: Dict[str, Any] = {}
        description_payload = Scenarios._build_description_payload(summary)
        if description_payload:
            patch_payload.update(description_payload)
        if extras:
            patch_payload["extras"] = extras
        if patch_payload:
            logger.info(f"Patching created scenario {created['id']} with description/extras")
            await Scenarios.update_scenario(client, created["id"], patch_payload)

        return created

    @staticmethod
    async def update_native_api_scenario(
        client: AttackIQClient,
        scenario_id: str,
        *,
        apis: Optional[list[Dict[str, Any]]] = None,
        summary: Optional[str] = None,
        extras: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        scenario = await Scenarios.get_scenario(client, scenario_id)
        if not scenario:
            raise ValueError(f"Scenario not found: {scenario_id}")

        existing_model = scenario.get("model_json") or {}
        model_json = Scenarios.build_native_api_model_json(
            base_model_json=existing_model,
            apis=apis if apis is not None else existing_model.get("apis") or [],
        )

        payload: Dict[str, Any] = {"model_json": model_json}
        description_payload = Scenarios._build_description_payload(summary)
        if description_payload:
            payload.update(description_payload)
        if extras:
            payload["extras"] = extras
        if not payload:
            raise ValueError("No updates specified for scenario")

        logger.info(f"Updating Native API scenario {scenario_id}")
        updated = await Scenarios.update_scenario(client, scenario_id, payload)
        return updated or await Scenarios.get_scenario(client, scenario_id)
