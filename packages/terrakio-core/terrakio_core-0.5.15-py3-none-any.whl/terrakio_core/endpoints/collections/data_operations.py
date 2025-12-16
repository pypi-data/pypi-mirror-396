import json
import os
from typing import Any, Dict, Optional, Union, Callable

import aiohttp

from ...exceptions import (
    CollectionNotFoundError,
    DownloadFilesError,
    GetTaskError,
    UploadArtifactsError,
    UploadRequestsError,
)
from ...helper.decorators import require_api_key


class DataOperationsMixin:
    """Data generation and processing operations."""
    
    @require_api_key
    async def upload_artifacts(
        self,
        collection: str,
        file_type: str,
        compressed: Optional[bool] = True
    ) -> Dict[str, Any]:
        """
        Retrieve signed url to upload artifact file to a collection.

        Args:
            collection: Name of collection
            file_type: The extension of the file
            compressed: Whether to compress the file using gzip or not (defaults to True)
        
        Returns:
            API response as a dictionary containing the upload URL

        Raises:
            CollectionNotFoundError: If the collection is not found
            UploadArtifactsError: If the API request fails due to unknown reasons
        """
        params = {
            "file_type": file_type,
            "compressed": str(compressed).lower(),
        }

        response, status = await self._client._terrakio_request("GET", f"collections/{collection}/upload/artifact", params=params)
        if status != 200:
            if status == 404:
                raise CollectionNotFoundError(f"Collection {collection} not found", status_code=status)
            raise UploadArtifactsError(f"Upload artifacts failed with status {status}", status_code=status)

        return response

    async def _get_upload_url(
        self,
        collection: str
    ) -> Dict[str, Any]:
        """
        Retrieve signed url to upload requests for a collection.

        Args:
            collection: Name of collection
        
        Returns:
            API response as a dictionary containing the upload URL

        Raises:
            CollectionNotFoundError: If the collection is not found
            UploadRequestsError: If the API request fails due to unknown reasons
        """
        response, status = await self._client._terrakio_request("GET", f"collections/{collection}/upload/requests")

        if status != 200:
            if status == 404:
                raise CollectionNotFoundError(f"Collection {collection} not found", status_code=status)
            raise UploadRequestsError(f"Upload requests failed with status {status}", status_code=status)

        return response

    @require_api_key
    async def _upload_file(self, file_path: str, url: str, use_gzip: bool = True):
        """
        Helper method to upload a JSON file to a signed URL.
        
        Args:
            file_path: Path to the JSON file
            url: Signed URL to upload to
            use_gzip: Whether to compress the file with gzip
        """
        try:
            with open(file_path, 'r') as file:
                json_data = json.load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"JSON file not found: {file_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in file {file_path}: {e}")
        
        return await self._upload_json_data(json_data, url, use_gzip)

    @require_api_key
    async def _upload_json_data(self, json_data, url: str, use_gzip: bool = True):
        """
        Helper method to upload JSON data directly to a signed URL.
        
        Args:
            json_data: JSON data (dict or list) to upload
            url: Signed URL to upload to
            use_gzip: Whether to compress the data with gzip
        """
        if hasattr(json, 'dumps') and 'ignore_nan' in json.dumps.__code__.co_varnames:
            dumps_kwargs = {'ignore_nan': True}
        else:
            dumps_kwargs = {}
        
        if use_gzip:
            import gzip
            body = gzip.compress(json.dumps(json_data, **dumps_kwargs).encode('utf-8'))
            headers = {
                'Content-Type': 'application/json',
                'Content-Encoding': 'gzip'
            }
        else:
            body = json.dumps(json_data, **dumps_kwargs).encode('utf-8')
            headers = {
                'Content-Type': 'application/json'
            }
        
        response = await self._client._regular_request("PUT", url, data=body, headers=headers)
        return response

    @require_api_key
    async def generate_data(
        self,
        collection: str,
        file_path: str,
        output: str,
        skip_existing: Optional[bool] = True,
        force_loc: Optional[bool] = None,
        server: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate data for a collection.

        Args:
            collection: Name of collection
            file_path: Path to the file to upload
            output: Output type (str)
            force_loc: Write data directly to the cloud under this folder
            skip_existing: Skip existing data
            server: Server to use
        
        Returns:
            API response as a dictionary containing task information

        Raises:
            CollectionNotFoundError: If the collection is not found
            GetTaskError: If the API request fails due to unknown reasons
        """
        
        await self.get_collection(collection = collection)

        upload_urls = await self._get_upload_url(
            collection = collection
        )
        
        url = upload_urls['url']

        await self._upload_file(file_path, url)
        
        payload = {"output": output, "skip_existing": skip_existing}
        
        if force_loc is not None:
            payload["force_loc"] = force_loc
        if server is not None:
            payload["server"] = server
        
        response, status = await self._client._terrakio_request("POST", f"collections/{collection}/generate_data", json=payload)

        if status != 200:
            if status == 404:
                raise CollectionNotFoundError(f"Collection {collection} not found", status_code=status)
            raise GetTaskError(f"Generate data failed with status {status}", status_code=status)
        
        return response

    @require_api_key
    async def post_processing(
        self,
        collection: str,
        folder: str,
        consumer: str,
        extra: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Run post processing for a collection.
        
        Args:
            collection: Name of collection
            folder: Folder to store output
            consumer: Path to post processing script
            extra: Optional JSON string for extra params (dict)
        
        Returns:
            API response as a dictionary containing task information
        
        Raises:
            CollectionNotFoundError: If the collection is not found
            GetTaskError: If the API request fails due to unknown reasons
        """
        await self.get_collection(collection=collection)
        
        with open(consumer, 'rb') as f:
            form = aiohttp.FormData()
            form.add_field('folder', folder)
            form.add_field(
                'consumer',
                f.read(),
                filename='consumer.py',
                content_type='text/x-python'
            )
            if extra is not None:
                form.add_field('extra', extra)
            
            response, status = await self._client._terrakio_request(
                "POST",
                f"collections/{collection}/post_process",
                data=form
            )
        
        if status != 200:
            if status == 404:
                raise CollectionNotFoundError(
                    f"Collection {collection} not found",
                    status_code=status
                )
            raise GetTaskError(
                f"Post processing failed with status {status}",
                status_code=status
            )
        
        return response

    @require_api_key
    async def download_files(
        self,
        collection: str,
        file_type: str,
        page: Optional[int] = None,
        page_size: Optional[int] = 100,
        folder: Optional[str] = None,
        url: Optional[bool] = True,
        progress_callback: Optional[Callable] = None,
        path: Optional[str] = None,
        flatten: Optional[bool] = False
    ) -> Dict[str, Any]:
        """
        Get list of signed urls to download files in collection, or download the files directly.

        Args:
            collection: Name of collection
            file_type: Type of files to download - must be either 'raw' or 'processed'
            page: Page number (optional). If None, downloads all pages. If specified, downloads only that page.
            page_size: Number of files to return per page (optional, defaults to 100)
            folder: If processed file type, which folder to download files from (optional)
            url: If True, return signed URLs; if False, download files directly (optional, defaults to True)
            progress_callback: Optional callback function(current, total, status) for progress updates
            path: Directory path to download files to (optional, defaults to current directory)
            flatten: If True, download all files directly to path without creating subfolders (optional, defaults to False)

        Returns:
            API response as a dictionary containing list of download URLs (if url=True),
            or a dictionary with downloaded file information (if url=False)

        Raises:
            CollectionNotFoundError: If the collection is not found
            DownloadFilesError: If the API request fails due to unknown reasons
            ValueError: If file_type is not 'raw' or 'processed'
        """
        if file_type not in ['raw', 'processed']:
            raise ValueError(f"file_type must be either 'raw' or 'processed', got '{file_type}'")
        
        # Determine if we should download all pages or just one
        download_all_pages = (page is None)
        current_page = 0 if download_all_pages else page
        
        all_files = []
        
        # Fetch all file URLs first
        while True:
            params = {"file_type": file_type, "page": current_page}
            
            if page_size is not None:
                params["page_size"] = page_size
            if folder is not None:
                params["folder"] = folder

            response, status = await self._client._terrakio_request("GET", f"collections/{collection}/download", params=params)

            if status != 200:
                if status == 404:
                    raise CollectionNotFoundError(f"Collection {collection} not found", status_code=status)
                raise DownloadFilesError(f"Download files failed with status {status}", status_code=status)
            
            files = response.get('files', []) if isinstance(response, dict) else []
            
            if not files:
                break
            
            all_files.extend(files)
            
            # If user specified a specific page, only download that page
            if not download_all_pages:
                break
            
            current_page += 1
        
        if url:
            # Return URLs format matching original API response
            return {
                'collection': collection,
                'files': all_files,
                'total': len(all_files)
            }
        
        # Download all files with progress tracking
        downloaded_files = []
        total_files = len(all_files)
        
        # Use provided path or current directory
        base_path = path if path else "."
        
        async with aiohttp.ClientSession() as session:
            for idx, file_info in enumerate(all_files):
                try:
                    file_url = file_info.get('url')
                    filename = file_info.get('filename', file_info.get('file', '')) 
                    group = file_info.get('group', '')
                    
                    if progress_callback:
                        progress_callback(idx + 1, total_files, f"Downloading {filename}")
                    
                    if not file_url:
                        downloaded_files.append({
                            'filename': filename,
                            'group': group,
                            'error': 'No URL provided'
                        })
                        continue
                    
                    async with session.get(file_url) as file_response:
                        if file_response.status == 200:
                            content = await file_response.read()
                            
                            # Determine output directory based on flatten parameter
                            if flatten:
                                # Put all files directly in base_path
                                output_dir = base_path
                            else:
                                # Create subdirectories for groups
                                if group:
                                    output_dir = os.path.join(base_path, group)
                                else:
                                    output_dir = base_path
                            
                            os.makedirs(output_dir, exist_ok=True)
                            filepath = os.path.join(output_dir, filename)
                            
                            with open(filepath, 'wb') as f:
                                f.write(content)
                            
                            downloaded_files.append({
                                'filename': filename,
                                'group': group,
                                'filepath': filepath,
                                'size': len(content)
                            })
                        else:
                            downloaded_files.append({
                                'filename': filename,
                                'group': group,
                                'error': f"Failed to download: HTTP {file_response.status}"
                            })
                except Exception as e:
                    downloaded_files.append({
                        'filename': file_info.get('file', 'unknown'),
                        'group': file_info.get('group', ''),
                        'error': str(e)
                    })
        
        return {
            'collection': collection,
            'downloaded_files': downloaded_files,
            'total': len(downloaded_files)
        }

    @require_api_key
    async def gen_and_process(
        self,
        collection: str,
        requests_file: Union[str, Any],
        output: str,
        folder: str,
        consumer: Union[str, Any],
        extra: Optional[Dict[str, Any]] = None,
        force_loc: Optional[bool] = False,
        skip_existing: Optional[bool] = True,
        server: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate data and run post-processing in a single task.

        Args:
            collection: Name of collection
            requests_file: Path to JSON file or file object containing request configurations
            output: Output type (str)
            folder: Folder to store output
            consumer: Path to post processing script or file object
            extra: Additional configuration parameters (optional)
            force_loc: Write data directly to the cloud under this folder (optional, defaults to False)
            skip_existing: Skip existing data (optional, defaults to True)
            server: Server to use (optional)

        Returns:
            API response as a dictionary containing task information

        Raises:
            CollectionNotFoundError: If the collection is not found
            GetTaskError: If the API request fails due to unknown reasons
        """
        await self.get_collection(collection = collection)

        upload_urls = await self._get_upload_url(collection=collection)
        url = upload_urls['url']
        
        # Handle requests_file - either file path (str) or file object
        if isinstance(requests_file, str):
            await self._upload_file(requests_file, url)
        else:
            # File object - read JSON and upload directly
            json_data = json.load(requests_file)
            await self._upload_json_data(json_data, url)

        # Handle consumer - either file path (str) or file object
        if isinstance(consumer, str):
            with open(consumer, 'rb') as f:
                consumer_content = f.read()
        else:
            # Assume it's a file object
            consumer_content = consumer.read()
        
        form = aiohttp.FormData()
        form.add_field('output', output)
        form.add_field('force_loc', str(force_loc).lower())
        form.add_field('skip_existing', str(skip_existing).lower())
        
        if server is not None:
            form.add_field('server', server)
        
        form.add_field('extra', json.dumps(extra or {}))
        form.add_field('folder', folder)
        form.add_field(
            'consumer',
            consumer_content,
            filename='consumer.py',
            content_type='text/x-python'
        )
        
        response, status = await self._client._terrakio_request(
            "POST",
            f"collections/{collection}/gen_and_process",
            data=form
        )
        
        if status != 200:
            if status == 404:
                raise CollectionNotFoundError(f"Collection {collection} not found", status_code=status)
            raise GetTaskError(f"Gen and process failed with status {status}", status_code=status)

        return response
    
    @require_api_key
    async def combine_tiles(
        self,
        collection: str,
        file_path: str,
        output: str,
        max_file_size_mb: Optional[int] = 5120,
        dtype: Optional[str] = "float32",
        skip_existing: Optional[bool] = True,
        force_loc: Optional[bool] = None,
        server: Optional[str] = None
    ) -> Dict[str, Any]:
        
        if dtype not in ["float32", "uint8", "int8"]:
            raise ValueError(f"dtype must be one of 'float32', 'uint8', or 'int8', got '{dtype}'")
        
        if max_file_size_mb is not None and (max_file_size_mb <= 0 or max_file_size_mb > 50240):
            raise ValueError("max_file_size_mb must be a positive integer below 50240 (50 GB)")
        
        if output not in ["netcdf", "geotiff"]:
            raise ValueError(f"output must be either 'netcdf' or 'geotiff', got '{output}'")
        
        await self.get_collection(collection = collection)

        upload_urls = await self._get_upload_url(
            collection = collection
        )
        
        url = upload_urls['url']

        await self._upload_file(file_path, url)
        
        payload = {
            "dtype": dtype, 
            "max_file_size_mb": max_file_size_mb,
            "output": output, 
            "skip_existing": skip_existing
        }
        
        if force_loc is not None:
            payload["force_loc"] = force_loc
        if server is not None:
            payload["server"] = server
        
        response, status = await self._client._terrakio_request("POST", f"collections/{collection}/combine_tiles", json=payload)

        if status != 200:
            if status == 404:
                raise CollectionNotFoundError(f"Collection {collection} not found", status_code=status)
            raise GetTaskError(f"Generate data failed with status {status}", status_code=status)
        
        return response
        
        

    @require_api_key
    async def upload_artifact_file(
        self,
        collection: str,
        file_path: str,
        file_type: str,
        compressed: Optional[bool] = True
    ) -> Dict[str, Any]:
        """
        Upload an artifact file to a collection.

        Args:
            collection: Name of collection
            file_path: Path to the file to upload
            file_type: The extension of the file
            compressed: Whether to compress the file using gzip or not (defaults to True)
        
        Returns:
            API response from the upload operation

        Raises:
            CollectionNotFoundError: If the collection is not found
            UploadArtifactsError: If the API request fails due to unknown reasons
            FileNotFoundError: If the file is not found
        """
        await self.get_collection(collection=collection)
        upload_info = await self.upload_artifacts(
            collection=collection,
            file_type=file_type,
            compressed=compressed
        )
        url = upload_info['url']
        await self._upload_file(file_path, url, use_gzip=compressed)
