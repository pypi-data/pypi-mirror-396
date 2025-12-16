import asyncio
import time
from typing import Optional, Dict, Any, List, AsyncGenerator

import httpx

from aiq_platform_api.core.async_utils import async_islice
from aiq_platform_api.core.client import AttackIQClient
from aiq_platform_api.core.constants import AssessmentExecutionStrategy
from aiq_platform_api.core.logger import AttackIQLogger

logger = AttackIQLogger.get_logger(__name__)


class Assessments:
    ASSESSMENT_ENDPOINT = "v1/assessments"
    PUBLIC_ENDPOINT = "v1/public/assessment"
    RESULTS_V1_ENDPOINT = "v1/results"
    RESULTS_V2_ENDPOINT = "v2/results"
    RUN_ASSESSMENT_V1_ENDPOINT = "v1/assessments/{}/run_all"
    RUN_ASSESSMENT_V2_ENDPOINT = "v2/assessments/{}/run_all"

    @staticmethod
    async def get_assessments(
        client: AttackIQClient,
        params: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = 10,
        offset: Optional[int] = 0,
        ordering: Optional[str] = "-modified",
    ) -> AsyncGenerator[Dict[str, Any], None]:
        request_params = params.copy() if params else {}
        if ordering:
            request_params["ordering"] = ordering
        logger.info(f"Listing assessments with params: {request_params}, limit: {limit}, offset: {offset}")
        generator = client.get_all_objects(Assessments.ASSESSMENT_ENDPOINT, params=request_params)
        stop = None if limit is None else offset + limit
        async for assessment in async_islice(generator, offset, stop):
            yield assessment

    @staticmethod
    async def _fetch_atomic_tests(
        client: AttackIQClient,
        assessment_id: str,
        scenarios_limit: Optional[int] = None,
    ) -> tuple[List[Dict[str, Any]], int, bool]:
        tests = [test async for test in client.get_all_objects("v1/tests", {"project_id": assessment_id})]

        scenarios_fetched = 0
        limit_reached = False

        for test in tests:
            if limit_reached:
                # Don't fetch more tests once limit is reached
                test["scenarios"] = []
                test["assets"] = []
                continue

            test_id = test["id"]

            # Fetch scenarios with optional limit
            scenarios = []
            async for scenario in client.get_all_objects("v1/test_scenarios", {"scenario_master_job": test_id}):
                # Check limit BEFORE appending so limit=0 fetches nothing
                if scenarios_limit is not None and scenarios_fetched >= scenarios_limit:
                    limit_reached = True
                    break  # Stop fetching scenarios
                scenarios.append(scenario)
                scenarios_fetched += 1
            test["scenarios"] = scenarios

            # Only fetch assets if we fetched scenarios for this test
            if scenarios:
                test["assets"] = [
                    asset async for asset in client.get_all_objects("v1/test_assets", {"scenario_master_job": test_id})
                ]
            else:
                test["assets"] = []

        return tests, scenarios_fetched, limit_reached

    @staticmethod
    def _compute_atomic_analysis(tests: List[Dict], version: int, boundaries: List) -> Dict[str, Any]:
        total_scenarios = sum(len(t.get("scenarios", [])) for t in tests)
        total_assets = sum(len(t.get("assets", [])) for t in tests)
        has_multi_asset = any(
            s.get("scenario", {}).get("is_multi_asset") for t in tests for s in t.get("scenarios", [])
        )
        is_network = bool(boundaries) and has_multi_asset

        if is_network:
            assessment_type = f"v{version} Atomic Network"
            estimated_jobs = total_scenarios * len(boundaries)
        else:
            assessment_type = f"v{version} Atomic Endpoint"
            estimated_jobs = sum(len(t.get("scenarios", [])) * max(len(t.get("assets", [])), 1) for t in tests)

        return {
            "assessment_type": assessment_type,
            "is_attack_graph": False,
            "is_network": is_network,
            "has_multi_asset_scenarios": has_multi_asset,
            "total_scenarios": total_scenarios,
            "total_assets": total_assets,
            "total_boundaries": len(boundaries) if is_network else 0,
            "estimated_jobs": estimated_jobs,
        }

    @staticmethod
    async def _fetch_attack_graph(
        client: AttackIQClient,
        assessment_id: str,
        nodes_limit: Optional[int] = None,
    ) -> Optional[Dict[str, Any]]:
        extra_url = client._build_url("v1/assessments/details", {"project_ids": assessment_id})
        extra = await client._make_request(extra_url, method="get", json=None)
        attack_graph_id = extra.get("results", {}).get(assessment_id, {}).get("attack_graph_id") if extra else None
        if not attack_graph_id:
            return None

        graph = await client.get_object(f"v1/attack_graphs/{attack_graph_id}")
        if not graph or nodes_limit is None:
            return graph

        # Apply nodes limit to the graph
        graph_data = graph.get("graph", {})
        nodes = graph_data.get("graph", {})
        total_nodes = len(nodes)

        if total_nodes > nodes_limit:
            # Keep only first N nodes (by key order)
            limited_keys = list(nodes.keys())[:nodes_limit]
            limited_nodes = {k: nodes[k] for k in limited_keys}
            graph["graph"]["graph"] = limited_nodes
            graph["_truncated"] = True
            graph["_truncation_info"] = {
                "type": "nodes",
                "fetched": nodes_limit,
                "total": total_nodes,
                "limit": nodes_limit,
            }

        return graph

    @staticmethod
    def _compute_attack_graph_analysis(graph: Dict[str, Any]) -> Dict[str, Any]:
        graph_data = graph.get("graph", {})
        nodes = graph_data.get("graph", {})
        stages = graph_data.get("graph_meta", {}).get("stages", {})
        has_multi_asset = any(n.get("is_multi_asset") for n in nodes.values())
        graph_type = "MTAG" if has_multi_asset else "STAG"

        return {
            "assessment_type": f"Attack Graph {graph_type}",
            "is_attack_graph": True,
            "graph_type": graph_type,
            "total_nodes": len(nodes),
            "total_stages": len(stages),
            "has_multi_asset_nodes": has_multi_asset,
            "estimated_jobs": len(nodes),
        }

    @staticmethod
    async def get_assessment_by_id(
        client: AttackIQClient,
        assessment_id: str,
        include_tests: bool = False,
        scenarios_limit: Optional[int] = None,
    ) -> Optional[Dict[str, Any]]:
        endpoint = f"{Assessments.ASSESSMENT_ENDPOINT}/{assessment_id}"
        logger.info(f"Fetching assessment details for ID: {assessment_id}")
        details = await client.get_object(endpoint)

        if not include_tests or details is None:
            return details

        version = details.get("version", 1)
        boundaries = details.get("boundaries", [])

        if details.get("master_job_count", 0) > 0:
            tests, scenarios_fetched, was_truncated = await Assessments._fetch_atomic_tests(
                client, assessment_id, scenarios_limit=scenarios_limit
            )
            details["tests"] = tests
            details["_analysis"] = Assessments._compute_atomic_analysis(tests, version, boundaries)
            # Add truncation metadata
            if was_truncated:
                details["_truncated"] = True
                details["_truncation_info"] = {
                    "type": "scenarios",
                    "fetched": scenarios_fetched,
                    "limit": scenarios_limit,
                    # Note: actual total unknown since we stopped fetching early
                }
        else:
            graph = await Assessments._fetch_attack_graph(client, assessment_id, nodes_limit=scenarios_limit)
            if graph:
                details["attack_graph"] = graph
                analysis = Assessments._compute_attack_graph_analysis(graph)
                details["_analysis"] = analysis
                # Add truncation metadata for attack graphs
                # Note: _analysis describes the truncated data, _truncation_info has full totals
                if graph.get("_truncated"):
                    details["_truncated"] = True
                    details["_truncation_info"] = graph.get("_truncation_info", {})

        return details

    @staticmethod
    async def search_assessments(
        client: AttackIQClient,
        query: Optional[str] = None,
        version: Optional[int] = None,
        created_after: Optional[str] = None,
        modified_after: Optional[str] = None,
        execution_strategy: Optional[int] = None,
        user_id: Optional[str] = None,
        is_attack_graph: Optional[bool] = None,
        project_template_id: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
        ordering: str = "-modified",
    ) -> Dict[str, Any]:
        logger.info(f"Searching assessments: query='{query}', version={version}, limit={limit}, offset={offset}")
        params: Dict[str, Any] = {"page_size": limit, "offset": offset}
        if query:
            params["search"] = query
        if version is not None:
            params["version"] = version
        if created_after:
            params["created_after"] = created_after
        if modified_after:
            params["modified_after"] = modified_after
        if execution_strategy is not None:
            params["execution_strategy"] = execution_strategy
        if user_id:
            params["user_id"] = user_id
        if is_attack_graph is not None:
            params["is_attack_graph"] = str(is_attack_graph).lower()
        if project_template_id:
            params["project_template_id"] = project_template_id
        if ordering:
            params["ordering"] = ordering

        url = client._build_url(Assessments.ASSESSMENT_ENDPOINT, params)
        data = await client._make_request(url, method="get", json=None)
        total_count = data.get("count", 0)
        results = data.get("results", [])
        logger.info(f"Found {total_count} total assessments, returning {len(results)}")
        return {"count": total_count, "results": results}

    @staticmethod
    async def list_assessment_runs(
        client: AttackIQClient,
        assessment_id: str,
        limit: int = 20,
        offset: int = 0,
        ordering: str = "-created",
    ) -> Dict[str, Any]:
        logger.info(f"Listing runs for assessment {assessment_id}: limit={limit}, offset={offset}")
        endpoint = f"{Assessments.PUBLIC_ENDPOINT}/{assessment_id}/runs"
        params: Dict[str, Any] = {}
        if ordering:
            params["ordering"] = ordering

        generator = client.get_all_objects(endpoint, params=params)
        all_runs = [run async for run in generator]
        total_count = len(all_runs)
        results = all_runs[offset : offset + limit]
        logger.info(f"Found {len(results)} runs (total: {total_count}) for assessment {assessment_id}")
        return {"count": total_count, "results": results}

    @staticmethod
    async def search_assessment_runs(
        client: AttackIQClient,
        assessment_id: str,
        limit: int = 20,
        offset: int = 0,
        ordering: str = "-created",
    ) -> Dict[str, Any]:
        return await Assessments.list_assessment_runs(client, assessment_id, limit, offset, ordering)

    @staticmethod
    async def get_run(client: AttackIQClient, assessment_id: str, run_id: str) -> Optional[Dict[str, Any]]:
        endpoint = "v1/widgets/assessment_runs"
        params = {"project_id": assessment_id, "run_id": run_id}
        logger.debug(f"Getting run {run_id} for assessment {assessment_id}")

        try:
            results = await client.get_object(endpoint, params=params)
            if results and isinstance(results, dict):
                runs = results["results"]
                if runs:
                    return runs[0]
        except httpx.HTTPStatusError as e:
            if e.response is not None and e.response.status_code == 400:
                if "run does not exist" in e.response.text:
                    return None
            raise

        return None

    @staticmethod
    async def get_most_recent_run_status(
        client: AttackIQClient, assessment_id: str, without_detection: bool = True
    ) -> Optional[Dict[str, Any]]:
        logger.info(f"Getting most recent run status for assessment {assessment_id}")

        result = await Assessments.list_assessment_runs(client, assessment_id, limit=1)
        runs = result.get("results", [])
        if runs:
            run = runs[0]
            run_id = run.get("id")
            logger.info(f"Found most recent run: {run_id}")

            status = await Assessments.get_run_status(client, assessment_id, run_id, without_detection)
            if status:
                run.update(status)

            return run

        logger.warning(f"No runs found for assessment {assessment_id}")
        return None

    @staticmethod
    async def get_run_status(
        client: AttackIQClient,
        assessment_id: str,
        run_id: str,
        without_detection: bool = True,
    ) -> Optional[Dict[str, Any]]:
        logger.info(
            f"Checking status for run {run_id} of assessment {assessment_id} without detection: {without_detection}"
        )

        run = await Assessments.get_run(client, assessment_id, run_id)
        if not run:
            logger.warning(f"Run ID {run_id} not found for assessment {assessment_id}")
            return None

        scenario_jobs = run.get("scenario_jobs_in_progress", 0)
        integration_jobs = run.get("integration_jobs_in_progress", 0)

        scenario_jobs = 0 if scenario_jobs is False else scenario_jobs
        integration_jobs = 0 if integration_jobs is False else integration_jobs

        completed = scenario_jobs == 0 if without_detection else (scenario_jobs == 0 and integration_jobs == 0)

        return {
            "scenario_jobs_in_progress": scenario_jobs,
            "integration_jobs_in_progress": integration_jobs,
            "completed": completed,
            "total_count": run.get("total_count", 0),
            "done_count": run.get("done_count", 0),
            "sent_count": run.get("sent_count", 0),
            "pending_count": run.get("pending_count", 0),
            "cancelled_count": run.get("cancelled_count", 0),
        }

    @staticmethod
    async def is_run_complete(
        client: AttackIQClient,
        assessment_id: str,
        run_id: str,
        without_detection: bool = True,
    ) -> bool:
        status = await Assessments.get_run_status(client, assessment_id, run_id, without_detection)
        return status.get("completed", False) if status else False

    @staticmethod
    async def run_assessment(client: AttackIQClient, assessment_id: str, assessment_version: int) -> Optional[str]:
        endpoint = (
            Assessments.RUN_ASSESSMENT_V2_ENDPOINT
            if assessment_version == 2
            else Assessments.RUN_ASSESSMENT_V1_ENDPOINT
        ).format(assessment_id)

        run_result = await client.post_object(endpoint, data={})

        if not run_result:
            logger.error(f"Failed to start assessment {assessment_id}")
            return None

        run_id = run_result["run_id"]
        if not run_id:
            logger.error(f"No run ID in response for assessment {assessment_id}")
            return None

        logger.info(f"Assessment {assessment_id} (v{assessment_version}) started with run ID: {run_id}")
        return run_id

    @staticmethod
    async def get_results_by_run_id(
        client: AttackIQClient,
        run_id: str,
        assessment_version: int,
        limit: Optional[int] = 10,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        endpoint = Assessments.RESULTS_V2_ENDPOINT if assessment_version == 2 else Assessments.RESULTS_V1_ENDPOINT
        params = {"run_id": run_id, "assessment_results": "true"}
        logger.info(f"Fetching results for run ID: {run_id} from {endpoint}")

        generator = client.get_all_objects(endpoint, params=params)
        async for result in async_islice(generator, 0, limit):
            yield result

    @staticmethod
    async def get_result_details(
        client: AttackIQClient, result_id: str, assessment_version: int
    ) -> Optional[Dict[str, Any]]:
        base_endpoint = Assessments.RESULTS_V2_ENDPOINT if assessment_version == 2 else Assessments.RESULTS_V1_ENDPOINT
        endpoint = f"{base_endpoint}/{result_id}"
        logger.info(f"Fetching detailed result for ID: {result_id} from {endpoint}")
        return await client.get_object(endpoint)

    @staticmethod
    async def get_assets_in_assessment(
        client: AttackIQClient,
        assessment_id: str,
        limit: Optional[int] = 10,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        from aiq_platform_api.core.assets import Assets

        params = {"hide_hosted_agents": "true", "project_id": assessment_id}
        logger.info(f"Listing assets for assessment ID: {assessment_id}")
        generator = Assets.get_assets(client, params=params)
        async for asset in async_islice(generator, 0, limit):
            yield asset

    @staticmethod
    async def wait_for_run_completion(
        client: AttackIQClient,
        assessment_id: str,
        run_id: str,
        timeout: int = 600,
        check_interval: int = 10,
        without_detection: bool = True,
    ) -> bool:
        logger.info(
            f"Waiting for run {run_id} of assessment {assessment_id} to complete without detection: {without_detection}"
        )
        start_time = time.time()
        last_status = None

        while time.time() - start_time < timeout:
            run = await Assessments.get_run(client, assessment_id, run_id)
            if not run:
                logger.warning(f"Run {run_id} not found")
                return False

            scenario_jobs = run.get("scenario_jobs_in_progress", 0)
            integration_jobs = run.get("integration_jobs_in_progress", 0)

            total_count = run.get("total_count", 0)
            done_count = run.get("done_count", 0)

            if without_detection:
                is_completed = not scenario_jobs
            else:
                is_completed = not scenario_jobs and not integration_jobs

            if is_completed:
                elapsed_time = round(time.time() - start_time, 2)
                logger.info(f"Run completed in {elapsed_time} seconds")
                return True

            status_msg = f"Progress: {done_count}/{total_count} completed"
            if status_msg != last_status:
                logger.info(f"{status_msg}")
                last_status = status_msg

            await asyncio.sleep(check_interval)

        logger.warning(f"Run did not complete within {timeout} seconds")
        return False

    @staticmethod
    async def get_execution_strategy(client: AttackIQClient, assessment_id: str) -> AssessmentExecutionStrategy:
        endpoint = f"{Assessments.ASSESSMENT_ENDPOINT}/{assessment_id}"
        assessment = await client.get_object(endpoint)
        return AssessmentExecutionStrategy(assessment["execution_strategy"])

    @staticmethod
    async def set_execution_strategy(client: AttackIQClient, assessment_id: str, with_detection: bool) -> bool:
        execution_strategy = (
            AssessmentExecutionStrategy.WITH_DETECTION
            if with_detection
            else AssessmentExecutionStrategy.WITHOUT_DETECTION
        )
        endpoint = f"{Assessments.ASSESSMENT_ENDPOINT}/{assessment_id}"
        result = await client.patch_object(endpoint, {"execution_strategy": execution_strategy.value})
        return result is not None
