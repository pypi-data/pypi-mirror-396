import os
import tempfile
import time
import uuid
import json

from ..helper.tiles import tiles

async def create_dataset_file(
    client,
    aoi: str,
    expression: str,
    output: str,
    download_path: str,
    in_crs: str = "epsg:4326",
    to_crs: str | None = None,
    res: float = 0.0001,
    skip_existing: bool = False,
    name: str | None = None,
    poll_interval: int = 30,
    max_file_size_mb: int = 5120,
    dtype: str = "float32",
    tile_size: int = 1024,
    mask: bool = True
) -> dict:
    if not name:
        name = f"file-gen-{uuid.uuid4().hex[:8]}"
    
    reqs, groups = tiles(
        name = name, 
        aoi = aoi, 
        expression = expression,
        output = output,
        tile_size = tile_size,
        crs = in_crs,
        res = res,
        to_crs = to_crs,
        mask = mask,
    )

    await client.collections.create_collection(name)

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json') as requests_json:
        json.dump(reqs, requests_json, indent=2)
        requests_json.flush()
        combine_result = await client.collections.combine_tiles(name, requests_json.name, output, max_file_size_mb, dtype, skip_existing)

    combine_task_id = combine_result.get("task_id")
    client.logger.info(f"Tracking file generation task {combine_task_id} in collection {name}")
    await client.collections.track_progress(combine_task_id, poll_interval=poll_interval)

    if download_path:

        download_path = f"{download_path}/{name}"
        if not os.path.exists(download_path):
            os.makedirs(download_path, exist_ok=True)

        await client.collections.download_files(
            collection = name,
            file_type="processed",
            url=False,
            folder = "combined_files",
            flatten = True,
            path = download_path
        )
    else:
        client.logger.info(f"Dataset file/s available in collection {name} under 'combined_files' folder")
