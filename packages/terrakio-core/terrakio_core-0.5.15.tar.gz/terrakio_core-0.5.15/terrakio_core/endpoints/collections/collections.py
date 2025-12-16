from typing import Any, Dict, List, Optional

from ...exceptions import (
    CollectionAlreadyExistsError,
    CollectionNotFoundError,
    CreateCollectionError,
    DeleteCollectionError,
    GetCollectionError,
    InvalidCollectionTypeError,
    ListCollectionsError,
)
from ...helper.decorators import require_api_key


class CollectionsMixin:
    """Collection CRUD operations."""
    
    @require_api_key
    async def create_collection(
        self, 
        collection: str, 
        bucket: Optional[str] = None, 
        location: Optional[str] = None, 
        collection_type: str = "basic"
    ) -> Dict[str, Any]:
        """
        Create a collection for the current user.

        Args:
            collection: The name of the collection (required)
            bucket: The bucket to use (optional, admin only)
            location: The location to use (optional, admin only)
            collection_type: The type of collection to create (optional, defaults to "basic")
            
        Returns:
            API response as a dictionary containing the collection id
            
        Raises:
            CollectionAlreadyExistsError: If the collection already exists
            InvalidCollectionTypeError: If the collection type is invalid
            CreateCollectionError: If the API request fails due to unknown reasons
        """
        payload = {
            "collection_type": collection_type
        }
        
        if bucket is not None:
            payload["bucket"] = bucket
        
        if location is not None:
            payload["location"] = location
        
        response, status = await self._client._terrakio_request("POST", f"collections/{collection}", json=payload)
        if status != 200:
            if status == 400 or status == 409:
                raise CollectionAlreadyExistsError(f"Collection {collection} already exists", status_code=status)
            if status == 422:
                raise InvalidCollectionTypeError(f"Invalid collection type: {collection_type}", status_code=status)
            raise CreateCollectionError(f"Create collection failed with status {status}", status_code=status)

        return response

    @require_api_key
    async def get_collection(self, collection: str) -> Dict[str, Any]:
        """
        Get a collection by name.

        Args:
            collection: The name of the collection to retrieve(required)
            
        Returns:
            API response as a dictionary containing collection information
            
        Raises:
            CollectionNotFoundError: If the collection is not found
            GetCollectionError: If the API request fails due to unknown reasons
        """
        response, status = await self._client._terrakio_request("GET", f"collections/{collection}")

        if status != 200:
            if status == 404:
                raise CollectionNotFoundError(f"Collection {collection} not found", status_code=status)
            raise GetCollectionError(f"Get collection failed with status {status}", status_code=status)
        
        return response

    @require_api_key
    async def list_collections(
        self,
        collection_type: Optional[str] = None,
        limit: Optional[int] = 10,
        page: Optional[int] = 0
    ) -> List[Dict[str, Any]]:
        """
        List collections for the current user.

        Args:
            collection_type: Filter by collection type (optional)
            limit: Number of collections to return (optional, defaults to 10)
            page: Page number (optional, defaults to 0)
            
        Returns:
            API response as a list of dictionaries containing collection information
            
        Raises:
            ListCollectionsError: If the API request fails due to unknown reasons
        """
        params = {}
        
        if collection_type is not None:
            params["collection_type"] = collection_type
        
        if limit is not None:
            params["limit"] = limit
            
        if page is not None:
            params["page"] = page
        
        response, status = await self._client._terrakio_request("GET", "collections", params=params)

        if status != 200:
            raise ListCollectionsError(f"List collections failed with status {status}", status_code=status)
        
        return response

    @require_api_key
    async def delete_collection(
        self, 
        collection: str, 
        full: Optional[bool] = False, 
        outputs: Optional[list] = [], 
        data: Optional[bool] = False
    ) -> Dict[str, Any]:
        """
        Delete a collection by name.

        Args:
            collection: The name of the collection to delete (required)
            full: Delete the full collection (optional, defaults to False)
            outputs: Specific output folders to delete (optional, defaults to empty list)
            data: Whether to delete raw data (xdata folder) (optional, defaults to False)
            
        Returns:
            API response as a dictionary confirming deletion
            
        Raises:
            CollectionNotFoundError: If the collection is not found
            DeleteCollectionError: If the API request fails due to unknown reasons
        """
        params = {
            "full": str(full).lower(),
            "data": str(data).lower()
        }
        
        if outputs:
            params["outputs"] = outputs
        
        response, status = await self._client._terrakio_request("DELETE", f"collections/{collection}", params=params)

        if status != 200:
            if status == 404:
                raise CollectionNotFoundError(f"Collection {collection} not found", status_code=status)
            raise DeleteCollectionError(f"Delete collection failed with status {status}", status_code=status)

        return response

