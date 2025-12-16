from typing import Dict, Any
from datetime import datetime, timezone

from datasourcelib.core.sync_base import SyncBase
from datasourcelib.utils.logger import get_logger
from datasourcelib.indexes.azure_search_index import AzureSearchIndexer

logger = get_logger(__name__)


class FullLoadStrategy(SyncBase):
    """Full load: replace or reload entire source into vector DB."""

    def validate(self) -> bool:
        # Minimal validation: required keys exist on datasource
        try:
            return bool(self.data_source and self.data_source.validate_config())
        except Exception:
            logger.exception("FullLoadStrategy.validate failed")
            return False

    def sync(self, **kwargs) -> Dict[str, Any]:
        """
        Execute full load: read data from data_source and index into vector DB (Azure Search).
        Returns a dict with status, message and ISO timestamps.
        """
        started_at = datetime.now(timezone.utc).isoformat()
        try:
            logger.info("Running full data load (started_at=%s)", started_at)

            # Fetch data from configured data source
            data = self.data_source.fetch_data(**kwargs)

            # Log kwargs for debugging at debug level
            if kwargs:
                logger.debug("FullLoadStrategy.sync kwargs: %s", kwargs)

            # If no data returned, finish gracefully
            total_records = len(data) if isinstance(data, (list, tuple)) else (1 if data is not None else 0)
            if total_records == 0:
                finished_at = datetime.now(timezone.utc).isoformat()
                msg = "No records returned from data source"
                logger.info(msg)
                return {
                    "status": "success",
                    "message": msg,
                    "started_at": started_at,
                    "finished_at": finished_at,
                    "loaded_records": 0
                }

            # Use AzureSearchIndexer to create index and upload documents if requested
            indexer = AzureSearchIndexer(self.vector_db_config or {})
            if not indexer.validate_config():
                finished_at = datetime.now(timezone.utc).isoformat()
                msg = "Vector DB config invalid for Azure Search indexer"
                logger.error(msg)
                return {
                    "status": "failure",
                    "message": msg,
                    "started_at": started_at,
                    "finished_at": finished_at,
                    "loaded_records": 0
                }

            ok = indexer.index(data)
            if not ok:
                finished_at = datetime.now(timezone.utc).isoformat()
                msg = "Indexing data to Azure Search failed"
                logger.error(msg)
                return {
                    "status": "failure",
                    "message": msg,
                    "started_at": started_at,
                    "finished_at": finished_at,
                    "loaded_records": total_records
                }

            finished_at = datetime.now(timezone.utc).isoformat()
            msg = f"Full load completed. Loaded {total_records} records."
            logger.info("Full data load finished successfully (%s)", msg)
            return {
                "status": "success",
                "message": msg,
                "started_at": started_at,
                "finished_at": finished_at,
                "loaded_records": total_records
            }

        except Exception as ex:
            logger.exception("FullLoadStrategy.sync failed")
            finished_at = datetime.now(timezone.utc).isoformat()
            return {
                "status": "failure",
                "message": f"Exception: {ex}",
                "started_at": started_at,
                "finished_at": finished_at,
                "loaded_records": 0
            }