import json
from typing import Any, Dict, List, Optional

import geopandas as gpd
import pyproj

from ...exceptions import (
    CollectionNotFoundError,
    GetTaskError,
    QuotaInsufficientError,
)
from ...helper.decorators import require_api_key
from .common import (
    Dataset_Dtype,
    OutputTypes,
    get_bounds as _get_bounds,
    make_json_serializable as _make_json_serializable,
    tile_generator as _tile_generator,
    validate_date as _validate_date,
)


class DataGenerationMixin:
    """Data generation operations for collections."""

    @require_api_key
    async def training_samples(
        self,
        collection: str,
        aoi: str,
        expression_x: str,
        filter_x: str = "skip",
        filter_x_rate: float = 1,
        expression_y: str = "skip",
        filter_y: str = "skip",
        filter_y_rate: float = 1,
        samples: int = 1000,
        tile_size: float = 256,
        crs: str = "epsg:3577",
        res: float = 10,
        res_y: float = None,
        skip_test: bool = False,
        time_range: tuple[str, str] = None,
        time_precision: str = None,
        server: str = None,
        extra_filters: list[str] = None,
        extra_filters_rate: list[float] = None,
        extra_filters_res: list[float] = None,
        try_limit: int = 1000,
        allow_overlap: bool = True
    ) -> dict:
        """
        Generate an AI dataset using specified parameters.

        Args:
            collection: The collection name where we save the results
            aoi: Path to GeoJSON file containing area of interest
            expression_x: Expression for X data (features)
            filter_x: Filter expression for X data (default: "skip")
            filter_x_rate: Filter rate for X data (default: 1)
            expression_y: Expression for Y data (labels) (default: "skip")
            filter_y: Filter expression for Y data (default: "skip")
            filter_y_rate: Filter rate for Y data (default: 1)
            samples: Number of samples to generate (default: 1000)
            tile_size: Size of tiles in pixels (default: 256)
            crs: Coordinate reference system (default: "epsg:3577")
            res: Resolution for X data (default: 10)
            res_y: Resolution for Y data, defaults to res if None
            skip_test: Skip expression validation test (default: False)
            time_range: Tuple of (start_datetime, end_datetime) in ISO format (e.g., ("2023-01-01T00:00:00Z", "2025-01-01T00:00:00Z"))
            time_precision: Precision for random time sampling: 'year', 'month', 'day', 'hour', 'minute', or 'second'
            server: Server to use for processing
            extra_filters: Additional filter expressions
            extra_filters_rate: Rates for additional filters
            extra_filters_res: Resolutions for additional filters
            try_limit: Maximum consecutive retries when filters fail before terminating (default: 1000)
            allow_overlap: If False, samples cannot overlap with previously selected areas (default: True)

        Returns:
            Response containing task_id and collection name

        Raises:
            CollectionNotFoundError: If the collection is not found
            GetTaskError: If the API request fails
            TypeError: If extra filters have mismatched rate and resolution lists
            ValueError: If time_range or time_precision validation fails, or if try_limit is not positive
        """
        from datetime import datetime
        
        # Validate try_limit
        if try_limit < 1:
            raise ValueError(f"try_limit must be a positive integer, got {try_limit}")
        
        # Validate time_range and time_precision
        if (time_range is None) != (time_precision is None):
            raise ValueError("Both time_range and time_precision must be provided together, or both must be None")
        
        if time_precision is not None:
            valid_precisions = ['year', 'month', 'day', 'hour', 'minute', 'second']
            if time_precision not in valid_precisions:
                raise ValueError(f"time_precision must be one of {valid_precisions}, got '{time_precision}'")
        
        if time_range is not None:
            if not isinstance(time_range, (tuple, list)) or len(time_range) != 2:
                raise ValueError("time_range must be a tuple of (start_datetime, end_datetime)")
            
            # Validate ISO datetime format
            try:
                start_dt = datetime.fromisoformat(time_range[0].replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(time_range[1].replace('Z', '+00:00'))
                if start_dt >= end_dt:
                    raise ValueError(f"start_datetime ({time_range[0]}) must be before end_datetime ({time_range[1]})")
            except (ValueError, AttributeError) as e:
                raise ValueError(f"Invalid datetime format in time_range: {e}")
        
        expressions = [{"expr": expression_x, "res": res, "prefix": "x"}]
        
        res_y = res_y or res
        
        if expression_y != "skip":
            expressions.append({"expr": expression_y, "res": res_y, "prefix": "y"})
        
        filters = []
        if filter_x != "skip":
            filters.append({"expr": filter_x, "res": res, "rate": filter_x_rate})
        
        if filter_y != "skip":
            filters.append({"expr": filter_y, "res": res_y, "rate": filter_y_rate})
        
        if extra_filters:
            try:
                extra_filters_combined = zip(extra_filters, extra_filters_res, extra_filters_rate, strict=True)
            except TypeError:
                raise TypeError("Extra filters must have matching rate and resolution.")
            
            for expr, filter_res, rate in extra_filters_combined:
                filters.append({"expr": expr, "res": filter_res, "rate": rate})
        
        # Note: Template replacement for {year}, {month}, {day}, {hour}, etc. is now handled by the server
        # The server will randomly sample timestamps based on time_range and time_precision
        # and replace these placeholders for each sample
        
        if not skip_test:
            # For testing, we need to replace placeholders with valid test values
            # Use the start of the time_range as test values
            test_replacements = {}
            if time_range is not None:
                test_dt = datetime.fromisoformat(time_range[0].replace('Z', '+00:00'))
                test_replacements = {
                    "{year}": str(test_dt.year),
                    "{month}": str(test_dt.month),
                    "{day}": str(test_dt.day),
                    "{hour}": str(test_dt.hour),
                    "{minute}": str(test_dt.minute),
                    "{second}": str(test_dt.second)
                }
            
            for expr_dict in expressions:
                test_expr = expr_dict["expr"]
                for placeholder, value in test_replacements.items():
                    test_expr = test_expr.replace(placeholder, value)
                test_request = self._client.model._generate_test_request(test_expr, crs, -1)
                await self._client._terrakio_request("POST", "geoquery", json=test_request)
            
            for filter_dict in filters:
                test_expr = filter_dict["expr"]
                for placeholder, value in test_replacements.items():
                    test_expr = test_expr.replace(placeholder, value)
                test_request = self._client.model._generate_test_request(test_expr, crs, -1)
                await self._client._terrakio_request("POST", "geoquery", json=test_request)
        
        with open(aoi, 'r') as f:
            aoi_data = json.load(f)

        await self.get_collection(
            collection = collection,
        )

        payload = {
            "expressions": expressions,
            "filters": filters,
            "aoi": aoi_data,
            "samples": samples,
            "crs": crs,
            "tile_size": tile_size,
            "res": res,
            "output": "nc",
            "server": server,
            "try_limit": try_limit,
            "allow_overlap": allow_overlap
        }
        
        # Add time_range and time_precision if both are provided
        if time_range is not None and time_precision is not None:
            payload["time_range"] = list(time_range)  # Ensure it's a list for JSON serialization
            payload["time_precision"] = time_precision
        
        task_id_dict, status = await self._client._terrakio_request("POST", f"collections/{collection}/training_samples", json=payload)

        if status != 200:
            if status == 404:
                raise CollectionNotFoundError(f"Collection {collection} not found", status_code=status)
            raise GetTaskError(f"Training sample failed with status {status}", status_code=status)
        
        task_id = task_id_dict["task_id"]
        
        await self.track_progress(task_id)
        
        return {"task_id": task_id, "collection": collection}
            
    @require_api_key
    async def dataset(
        self,
        products: List[str],
        name: str,
        bucket: str = "terrakio",
        location: str = "testing/MSWXsmall",
        aoi: Optional[str] = None,
        expression: Optional[str] = None,
        date: Optional[str] = "2021-01-01",
        tile_size: float = 100,
        crs: str = "epsg:4326",
        res: float = 10,
        out_res: float = 10,
        no_data: float = -9999,
        dtype: str = "float32",
        create_doc: bool = False,
        skip_test: bool = False,
        force_res: bool = False,
        to_crs: Optional[str] = None,
        fully_cover: bool = True,
        skip_existing: bool = False,
    ) -> Dict[str, Any]:
        """
        Generate a dataset with the specified parameters.

        Args:
            products: List of product names
            name: Name of the dataset
            bucket: Storage bucket
            location: Storage location
            aoi: Path to GeoJSON file containing area of interest
            expression: Expression for data processing
            date: Date in YYYY-MM-DD format
            tile_size: Size of tiles (default: 100)
            crs: Coordinate reference system (default: "epsg:4326")
            res: Resolution (default: 10)
            out_res: Output resolution (default: 10)
            no_data: No data value (default: -9999)
            dtype: Data type (default: "float32")
            create_doc: Add dataset to the DB (default: False)
            skip_test: Skip testing the expression (default: False)
            force_res: Force resolution in case requests are too large (default: False)
            to_crs: Target coordinate reference system
            fully_cover: Fully cover the area (default: True)
            skip_existing: Skip existing data (default: False)

        Returns:
            Response containing task_id and collection name

        Raises:
            CollectionNotFoundError: If the collection is not found
            GetTaskError: If the API request fails
        """
        await self.create_collection(collection = name, bucket = bucket, location = location)
        date = _validate_date(date)
        sample = None
        reqs = []
        x_min, y_min, x_max, y_max, aoi_gdf = _get_bounds(aoi, crs, to_crs)
        if to_crs is None:
            to_crs = crs
        c=0
        for tile_req, i, j in _tile_generator(x_min, y_min, x_max, y_max, aoi_gdf, to_crs, res, tile_size, expression, OutputTypes.netcdf, fully_cover = fully_cover):
            c+=1
            if force_res:
                tile_req["force_res"] = True
            req_names = []
            for product in products:
                req_names.append(f"{product}_{date.strftime('%Y%m%d')}000000_{i:03d}_{j:03d}_00")
            reqs.append({"group": name, "file": req_names, "request": tile_req})
            if sample is None:
                sample = tile_req["expr"]
        i_max = int((x_max-x_min)/(tile_size*res))
        j_max = int((y_max-y_min)/(tile_size*res))
        geot = [x_min, out_res, 0, y_max, 0, -out_res]
        if not skip_test:
            result = await self._client.geoquery(**reqs[0]["request"], debug = "requests")
            request_count = result.get('request_count', 0)

        user_quota = await self._client.auth.get_user_quota()
        user_quota = user_quota.get('quota', -9999)
        
        if user_quota !=-9999 and user_quota < len(reqs) * request_count:
            raise QuotaInsufficientError(f"User quota is insufficient. Please contact support to increase your quota.")

        upload_urls = await self._get_upload_url(collection=name)
        url = upload_urls['url']
        await self._upload_json_data(reqs, url, use_gzip=True)

        payload = {"output": "snp", "skip_existing": skip_existing, "dtype": dtype, "no_data": no_data}
        
        task_id, status = await self._client._terrakio_request("POST", f"collections/{name}/generate_data", json=payload)
        task_id = task_id["task_id"]
        if dtype == Dataset_Dtype.uint8.value:
            no_data = int(no_data)
        if create_doc:
            await self._client.datasets.create_dataset(
                name=name,
                products=products,
                dates_iso8601=[date.isoformat()],
                proj4=pyproj.CRS.to_proj4(aoi_gdf.crs),
                i_max=i_max,
                j_max=j_max,
                x_size=int((res*tile_size)/out_res),
                y_size=int((res*tile_size)/out_res),
                geotransform=geot,
                no_data=no_data,
                data_type=dtype,
                bucket=bucket,
                path=f"{location}/%s_%s_%03d_%03d_%02d.snp",
                max_zoom=0,
            )

        await self.track_progress(task_id)

    @require_api_key
    async def tiles(
        self,
        collection: str,
        name: str = "irrigation_2019",
        aoi: Optional[str] = None,
        expression: str = "NSWIrrigation.landuse@(year=2019)",
        output: OutputTypes = OutputTypes.netcdf,
        tile_size: float = 10000,
        crs: str = "epsg:3577",
        res: float = 10,
        skip_test: bool = False,
        force_res: bool = False,
        to_crs: Optional[str] = None,
        fully_cover: bool = True,
        skip_existing: bool = False,
    ) -> Dict[str, Any]:
        """
        Generate tiles with the specified parameters.

        Args:
            collection: Name of the collection
            name: Name of the dataset (default: "irrigation_2019")
            aoi: Path to GeoJSON file containing area of interest
            expression: Expression for data processing (default: "NSWIrrigation.landuse@(year=2019)")
            output: Output format (default: "netcdf")
            tile_size: Size of tiles (default: 10000)
            crs: Coordinate reference system (default: "epsg:3577")
            res: Resolution (default: 10)
            skip_test: Skip testing the expression (default: False)
            force_res: Force resolution in case requests are too large (default: False)
            to_crs: Target coordinate reference system
            fully_cover: Fully cover the area (default: True)
            skip_existing: Skip existing data (default: False)

        Returns:
            Response containing task_id

        Raises:
            CollectionNotFoundError: If the collection is not found
            GetTaskError: If the API request fails
        """
        

        await self.get_collection(collection=collection)

        reqs = []
        sample = None
        x_min, y_min, x_max, y_max, aoi_gdf = _get_bounds(aoi, crs, to_crs)
        if to_crs is None:
            to_crs = crs
        for tile_req, i, j in _tile_generator(x_min, y_min, x_max, y_max, aoi_gdf, to_crs, res, tile_size, expression, output, fully_cover):
            if force_res:  
                tile_req["force_res"] = True
            req_name = f"{name}_{i:02d}_{j:02d}"
            reqs.append({"group": "tiles", "file": req_name, "request": tile_req})
            if sample is None:
                sample = tile_req["expr"]

        if not skip_test:
            result = await self._client.geoquery(**reqs[0]["request"], debug = "requests")
            request_count = result.get('request_count', 0)

        user_quota = await self._client.auth.get_user_quota()
        user_quota = user_quota.get('quota', -9999)
        
        if user_quota !=-9999 and user_quota < len(reqs) * request_count:
            raise QuotaInsufficientError(f"User quota is insufficient. Please contact support to increase your quota.")

        count = len(reqs)
        groups = list(set(dic["group"] for dic in reqs))
        self.console.print(f"[green]{count}[/green] requests with [blue]{len(groups)}[/blue] groups identified.")
        upload_urls = await self._get_upload_url(collection=collection)
        url = upload_urls['url']
        await self._upload_json_data(reqs, url, use_gzip=True)

        payload = {"output": output.value, "skip_existing": skip_existing}
        
        task_id, status = await self._client._terrakio_request("POST", f"collections/{collection}/generate_data", json=payload)
        task_id = task_id["task_id"]

        await self.track_progress(task_id)

    @require_api_key
    async def polygons(
        self,
        collection: str,
        aoi: str,
        expression: str = "mean:space(MSWX.air_temperature@(year=2022))",
        output: OutputTypes = OutputTypes.netcdf,
        id_field: str = "GID_0",
        crs: str = "epsg:4326",
        res: float = -1,
        skip_test: bool = False,
        skip_existing: bool = False,
    ) -> Dict[str, Any]:
        """
        Generate mass-stats for polygons in a GeoJSON file using the same expression.

        Args:
            collection: Name of the collection
            name: Name of the dataset
            aoi: Path to GeoJSON file containing area of interest
            expression: Expression for data processing (default: "mean:space(MSWX.air_temperature@(year=2022))")
            output: Output format (default: "netcdf")
            id_field: Field name to use as identifier (default: "GID_0")
            crs: Coordinate reference system (default: "epsg:4326")
            res: Resolution (default: -1)
            skip_test: Skip testing the expression (default: False)
            skip_existing: Skip existing data (default: False)

        Returns:
            Response containing task_id

        Raises:
            CollectionNotFoundError: If the collection is not found
            GetTaskError: If the API request fails
            ValueError: If id_field not found in feature properties or if id_field values are not unique
        """
        await self.get_collection(collection=collection)

        gdf = gpd.read_file(aoi)
        sample = None
        features = gdf.__geo_interface__
        reqs = []
        
        # Check if id_field exists and values are unique (fail-fast)
        seen = set()
        for feature in features["features"]:
            if id_field not in feature["properties"]:
                raise ValueError(f"ID field {id_field} not found in feature properties.")
            val = feature["properties"][id_field]
            if val in seen:
                raise ValueError(f"ID field '{id_field}' contains non-unique values. Please choose an id_field with unique values.")
            seen.add(val)
        
        for feature in features["features"]:
            feat = {
                "type": "Feature",
                "properties": {},
                "geometry": feature["geometry"],
            }
            request = {
                "feature": feat,
                "expr": expression,
                "output": output.value,
                "in_crs": crs, 
                "out_crs": crs,
                "resolution": res,
            }
            reqs.append({
                "group": "polygons", 
                "file": feature["properties"][id_field], 
                "request": request, 
                "metadata": _make_json_serializable(feature["properties"])
            })
            if sample is None:
                sample = request["expr"]

        # Test first request to ensure expression is valid
        if not skip_test:
            result = await self._client.geoquery(**reqs[0]["request"], debug="requests")
            request_count = result.get('request_count', 0)

        user_quota = await self._client.auth.get_user_quota()
        user_quota = user_quota.get('quota', -9999)
        
        if user_quota != -9999 and user_quota < len(reqs) * request_count:
            raise QuotaInsufficientError(f"User quota is insufficient. Please contact support to increase your quota.")
        
        count = len(reqs)
        groups = list(set(dic["group"] for dic in reqs))
        self.console.print(f"[green]{count}[/green] requests with [blue]{len(groups)}[/blue] groups identified.")
        upload_urls = await self._get_upload_url(collection=collection)
        url = upload_urls['url']
        await self._upload_json_data(reqs, url, use_gzip=True)

        payload = {"output": output.value, "skip_existing": skip_existing}
        
        task_id, status = await self._client._terrakio_request("POST", f"collections/{collection}/generate_data", json=payload)
        task_id = task_id["task_id"]

        await self.track_progress(task_id)

        return {"task_id": task_id, "collection": collection}

