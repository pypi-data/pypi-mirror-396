import os
from typing import Any, Dict, Optional

from ...exceptions import (
    CollectionNotFoundError,
    GetTaskError,
)
from ...helper.decorators import require_api_key


class ZonalStatsMixin:
    """Zonal statistics operations."""
    
    @require_api_key
    async def zonal_stats(
        self,
        collection: str,
        id_property: str,
        column_name: str,
        expr: str,
        resolution: Optional[int] = 1,
        in_crs: Optional[str] = "epsg:4326",
        out_crs: Optional[str] = "epsg:4326"
    ) -> Dict[str, Any]:
        """
        Run zonal stats over uploaded geojson collection.

        Args:
            collection: Name of collection
            id_property: Property key in geojson to use as id
            column_name: Name of new column to add
            expr: Terrak.io expression to evaluate
            resolution: Resolution of request (optional, defaults to 1)
            in_crs: CRS of geojson (optional, defaults to "epsg:4326")
            out_crs: Desired output CRS (optional, defaults to "epsg:4326")

        Returns:
            API response as a dictionary containing task information

        Raises:
            CollectionNotFoundError: If the collection is not found
            GetTaskError: If the API request fails due to unknown reasons
        """
        payload = {
            "id_property": id_property,
            "column_name": column_name,
            "expr": expr,
            "resolution": resolution,
            "in_crs": in_crs,
            "out_crs": out_crs
        }
        
        response, status = await self._client._terrakio_request("POST", f"collections/{collection}/zonal_stats", json=payload)

        if status != 200:
            if status == 404:
                raise CollectionNotFoundError(f"Collection {collection} not found", status_code=status)
            raise GetTaskError(f"Zonal stats failed with status {status}", status_code=status)
        
        return response

    @require_api_key
    async def zonal_stats_transform(
        self,
        collection: str,
        consumer: str
    ) -> Dict[str, Any]:
        """
        Transform raw data in collection. Creates a new collection.

        Args:
            collection: Name of collection
            consumer: Post processing script (file path or script content)

        Returns:
            API response as a dictionary containing task information

        Raises:
            CollectionNotFoundError: If the collection is not found
            GetTaskError: If the API request fails due to unknown reasons
        """
        if os.path.isfile(consumer):
            with open(consumer, 'r') as f:
                script_content = f.read()
        else:
            script_content = consumer

        files = {
            'consumer': ('script.py', script_content, 'text/plain')
        }
        
        response, status = await self._client._terrakio_request(
            "POST", 
            f"collections/{collection}/transform", 
            files=files
        )

        if status != 200:
            if status == 404:
                raise CollectionNotFoundError(f"Collection {collection} not found", status_code=status)
            raise GetTaskError(f"Transform failed with status {status}", status_code=status)
        
        return response

