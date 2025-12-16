from typing import Optional, Dict, Any, AsyncGenerator

from aiq_platform_api.core.async_utils import async_islice
from aiq_platform_api.core.client import AttackIQClient
from aiq_platform_api.core.constants import AssetStatus
from aiq_platform_api.core.logger import AttackIQLogger
from aiq_platform_api.core.tags import TaggedItems

logger = AttackIQLogger.get_logger(__name__)


class Assets:
    """Utilities for working with assets a.k.a Test Points

    API Endpoint: /v1/assets, /v1/asset_jobs
    """

    ENDPOINT = "v1/assets"
    ASSET_JOBS_ENDPOINT = "v1/asset_jobs"
    JOB_NAME_DESTROY_SELF = "06230502-890c-4dca-aab1-296706758fd9"

    @staticmethod
    async def get_assets(
        client: AttackIQClient,
        params: dict = None,
        limit: Optional[int] = 10,
        offset: Optional[int] = 0,
        ordering: Optional[str] = "-modified",
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """List assets with minimal fields (63.3% reduction: 30 -> 11 fields), ordering, and offset support.

        Args:
            ordering: Sort order (default: -modified for most recent first)
                     Use '-' prefix for descending (e.g., '-modified', '-created')
                     Omit '-' for ascending (e.g., 'modified', 'created', 'hostname')
        """
        request_params = params.copy() if params else {}
        request_params["minimal"] = "true"
        if "ordering" not in request_params and ordering:
            request_params["ordering"] = ordering
        logger.info(f"Listing assets with params: {request_params}, limit: {limit}, offset: {offset}")
        generator = client.get_all_objects(Assets.ENDPOINT, params=request_params)
        stop = offset + limit if limit is not None else None
        async for asset in async_islice(generator, offset, stop):
            yield asset

    @staticmethod
    async def get_asset_by_id(client: AttackIQClient, asset_id: str):
        """Get a specific asset by its ID."""
        return await client.get_object(f"{Assets.ENDPOINT}/{asset_id}")

    @staticmethod
    async def get_asset_by_hostname(client: AttackIQClient, hostname: str) -> Optional[Dict[str, Any]]:
        """Get a specific asset by its hostname."""
        params = {"hostname": hostname}
        assets = [asset async for asset in client.get_all_objects(Assets.ENDPOINT, params=params)]
        return assets[0] if assets else None

    @staticmethod
    async def search_assets(
        client: AttackIQClient,
        query: Optional[str] = None,
        limit: Optional[int] = 20,
        offset: Optional[int] = 0,
        ordering: Optional[str] = "-modified",
    ) -> dict:
        """Search or list assets.
        - With query: Search by keyword
        - Without query: List all assets (paginated)
        Returns {"count": total, "results": [...]}

        Args:
            ordering: Sort order (default: -modified for most recent first)
                     Use '-' prefix for descending (e.g., '-modified', '-created')
                     Omit '-' for ascending (e.g., 'modified', 'created', 'hostname')
        """
        logger.info(f"Searching assets with query: '{query}', limit: {limit}, offset: {offset}, ordering: {ordering}")
        params = {"minimal": "true", "limit": limit, "offset": offset}
        if query:
            params["search"] = query
        if "ordering" not in params and ordering:
            params["ordering"] = ordering
        url = client._build_url(Assets.ENDPOINT, params)
        data = await client._make_request(url, method="get", json=None)
        total_count = data.get("count", 0)
        results = data.get("results", [])
        logger.info(f"Found {total_count} total assets matching '{query}', returning {len(results)}")
        return {"count": total_count, "results": results}

    @staticmethod
    async def uninstall_asset(client: AttackIQClient, asset_id: str) -> bool:
        """Submit a job to uninstall an asset."""
        logger.info(f"Uninstalling asset with ID: {asset_id}")
        payload = {
            "asset": asset_id,
            "job_name": Assets.JOB_NAME_DESTROY_SELF,
            "one_way": True,
        }
        try:
            response = await client.post_object(Assets.ASSET_JOBS_ENDPOINT, data=payload)
            if response:
                logger.info(f"Asset {asset_id} uninstall job submitted successfully")
                return True
            logger.error(f"Failed to submit uninstall job for asset {asset_id}")
            return False
        except Exception as e:  # noqa: BLE001
            logger.error(f"Error while uninstalling asset {asset_id}: {str(e)}")
            return False

    @staticmethod
    async def add_tag(client: AttackIQClient, asset_id: str, tag_id: str) -> str:
        """Add a tag to an asset."""
        return await TaggedItems.create_tagged_item(client, "asset", asset_id, tag_id)

    @staticmethod
    async def get_total_assets(client: AttackIQClient) -> Optional[int]:
        """Get the total number of assets."""
        logger.info("Fetching total number of assets...")
        return await client.get_total_objects_count(Assets.ENDPOINT)

    @staticmethod
    async def get_assets_count_by_status(client: AttackIQClient, status: AssetStatus) -> Optional[int]:
        """Get the count of assets with a specific status."""
        logger.info(f"Fetching count of assets with status: {status.value}...")
        params = {"status": status.value}
        return await client.get_total_objects_count(Assets.ENDPOINT, params=params)

    @staticmethod
    async def get_active_assets_with_details(
        client: AttackIQClient, limit: Optional[int] = 10, offset: Optional[int] = 0
    ) -> list:
        """Get active assets with OS and agent details with pagination support."""
        params = {"status": AssetStatus.ACTIVE.value}
        assets = []

        async for asset in Assets.get_assets(client, params=params, limit=limit, offset=offset):
            assets.append(
                {
                    "id": asset.get("id"),
                    "hostname": asset.get("hostname"),
                    "product_name": asset.get("product_name", "unknown"),
                    "agent_version": asset.get("agent_version", "unknown"),
                    "ipv4_address": asset.get("ipv4_address"),
                    "ipv6_address": asset.get("ipv6_address"),
                    "mac_address": asset.get("mac_address"),
                    "domain_name": asset.get("domain_name"),
                    "processor_arch": asset.get("processor_arch"),
                    "status": asset.get("status"),
                    "deployment_state": asset.get("deployment_state"),
                    "modified": asset.get("modified"),
                }
            )

        logger.info(f"Retrieved {len(assets)} active assets")
        return assets
