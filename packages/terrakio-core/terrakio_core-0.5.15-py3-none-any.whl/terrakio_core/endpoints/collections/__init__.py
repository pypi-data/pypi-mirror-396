from rich.console import Console

from .collections import CollectionsMixin
from .common import Dataset_Dtype, OutputTypes, Region, regions
from .data_operations import DataOperationsMixin
from .generation import DataGenerationMixin
from .ingestion import IngestionMixin
from .tasks import TasksMixin
from .zonal_stats import ZonalStatsMixin

# Import methods directly for better IDE navigation support
from .collections import (
    CollectionsMixin as _CollectionsMixin,
)
from .tasks import (
    TasksMixin as _TasksMixin,
)
from .data_operations import (
    DataOperationsMixin as _DataOperationsMixin,
)
from .zonal_stats import (
    ZonalStatsMixin as _ZonalStatsMixin,
)
from .ingestion import (
    IngestionMixin as _IngestionMixin,
)
from .generation import (
    DataGenerationMixin as _DataGenerationMixin,
)


class Collections(
    CollectionsMixin,
    TasksMixin,
    DataOperationsMixin,
    ZonalStatsMixin,
    DataGenerationMixin,
    IngestionMixin
):
    """
    Collections and collection management client.
    
    This class provides methods for managing collections, tasks, data operations,
    zonal statistics, data generation, and ingestion operations.
    
    All methods are inherited from the following mixins:
    - CollectionsMixin: Collection CRUD operations (create_collection, get_collection, list_collections, delete_collection)
    - TasksMixin: Task management operations (track_progress, list_tasks, get_task, cancel_task, etc.)
    - DataOperationsMixin: Data generation and processing (generate_data, post_processing, gen_and_process, download_files, upload_artifacts)
    - ZonalStatsMixin: Zonal statistics operations (zonal_stats, zonal_stats_transform)
    - DataGenerationMixin: Data generation operations (training_samples, dataset, tiles, polygons)
    - IngestionMixin: Data ingestion and visualization (create_pyramids, tif)
    
    Note: Methods are defined in their respective mixin modules:
    - Collection methods: .collections module
    - Task methods: .tasks module
    - Data operation methods: .data_operations module
    - Zonal stats methods: .zonal_stats module
    - Data generation methods: .generation module
    - Ingestion methods: .ingestion module
    """
    
    def __init__(self, client):
        self._client = client
        self.console = Console()
        self.OutputTypes = OutputTypes
        self.Region = Region
        self.regions = regions
        self.Dataset_Dtype = Dataset_Dtype

# Explicitly re-export for better IDE support
__all__ = ['Collections', 'OutputTypes', 'Region', 'Dataset_Dtype', 'regions']
