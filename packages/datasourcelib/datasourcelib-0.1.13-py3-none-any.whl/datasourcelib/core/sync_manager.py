from typing import Dict, Any
from datetime import datetime
from .sync_types import SyncType, SyncStatus 
from ..datasources.datasource_types import DataSourceType
from ..utils.logger import get_logger
from ..utils.exceptions import SyncStrategyNotFound, DataSourceNotFound

# Import data sources
from ..datasources.sql_source import SQLDataSource
from ..datasources.azure_devops_source import AzureDevOpsSource
from ..datasources.sharepoint_source import SharePointSource
from ..datasources.blob_source import BlobStorageSource
from ..datasources.dataverse_source import DataverseSource

# concrete strategies
from datasourcelib.strategies.full_load import FullLoadStrategy
from datasourcelib.strategies.incremental_load import IncrementalLoadStrategy
from datasourcelib.strategies.timerange_load import TimeRangeLoadStrategy
from datasourcelib.strategies.daily_load import DailyLoadStrategy
from datasourcelib.strategies.ondemand_load import OnDemandLoadStrategy

logger = get_logger(__name__)

class SyncManager:
    """High-level manager to select and execute a sync strategy with data source."""

    _strategy_map = {
        SyncType.FULL: FullLoadStrategy,
        SyncType.INCREMENTAL: IncrementalLoadStrategy,
        SyncType.TIMERANGE: TimeRangeLoadStrategy,
        SyncType.DAILY: DailyLoadStrategy,
        SyncType.ONDEMAND: OnDemandLoadStrategy,
    }

    _datasource_map = {
        DataSourceType.SQL: SQLDataSource,
        DataSourceType.AZURE_DEVOPS: AzureDevOpsSource, 
        DataSourceType.SHAREPOINT: SharePointSource,
        DataSourceType.BLOB_STORAGE: BlobStorageSource,
        DataSourceType.Dataverse: DataverseSource
    }

    def execute_sync(self, sync_type: str, 
                    source_type: str,
                    source_config: Dict[str, Any],
                    vector_db_config: Dict[str, Any], 
                    **kwargs) -> Dict[str, Any]:
        start = datetime.utcnow()
        logger.info(f"Execute {sync_type} sync using {source_type} source")
        
        try:
            # validate and convert sync_type and source_type to their Enum members
            def _to_enum(enum_cls, val, label):
                if isinstance(val, enum_cls):
                    return val
                s = str(val)
                # case-insensitive name match
                for member in enum_cls:
                    if member.name.lower() == s.lower():
                        return member
                # try by value
                try:
                    return enum_cls(val)
                except Exception:
                    names = ", ".join([m.name for m in enum_cls])
                    values = ", ".join([str(m.value) for m in enum_cls])
                    raise ValueError(f"Invalid {label}. Permitted names: {names}. Permitted values: {values}")

            try:
                sync_type = _to_enum(SyncType, sync_type, "sync_type")
                source_type = _to_enum(DataSourceType, source_type, "source_type")
            except ValueError as ex:
                logger.error(str(ex))
                return {
                    "status": SyncStatus.FAILED,
                    "message": str(ex),
                    "started_at": start
                }
            # Get data source class
            source_cls = self._datasource_map.get(source_type)
            if not source_cls:
                raise DataSourceNotFound(f"No source registered for {source_type}")

            # Initialize data source
            data_source = source_cls(source_config)
            if not data_source.validate_config():
                raise ValueError("Invalid data source configuration")

            # Get sync strategy
            strategy_cls = self._strategy_map.get(sync_type)
            if not strategy_cls:
                raise SyncStrategyNotFound(f"No strategy for {sync_type}")

            # Initialize strategy with data source
            strategy = strategy_cls(data_source=data_source, 
                                 vector_db_config=vector_db_config)

            if not strategy.validate():
                message = "Strategy validation failed"
                logger.error(message)
                return {
                    "status": SyncStatus.FAILED,
                    "message": message,
                    "started_at": start
                }

            # Execute sync
            return strategy.sync(**kwargs)

        except Exception as ex:
            logger.exception("SyncManager.execute_sync failed")
            return {
                "status": SyncStatus.FAILED, 
                "message": str(ex),
                "started_at": start,
                "finished_at": datetime.utcnow()
            }