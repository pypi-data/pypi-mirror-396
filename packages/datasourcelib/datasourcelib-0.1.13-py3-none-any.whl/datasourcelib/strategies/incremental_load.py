from datetime import datetime, timezone
from datasourcelib.core.sync_base import SyncBase
from datasourcelib.utils.logger import get_logger
from typing import Dict, Any
logger = get_logger(__name__)

class IncrementalLoadStrategy(SyncBase):
    """Incremental load using last_sync timestamp or cursor."""

    def validate(self) -> bool:
        # require source to support incremental field or cursor
        if "cursor_field" not in self.source_config and "last_sync" not in self.source_config:
            logger.error("IncrementalLoadStrategy missing cursor_field or last_sync in source_config")
            return False
        return True

    def sync(self, last_sync: str = None, **kwargs) -> Dict[str, Any]:
        try:
            started_at = datetime.now(timezone.utc).isoformat()
            last = last_sync or self.source_config.get("last_sync")
            logger.info("Running incremental load since %s", last)
            # TODO: fetch delta rows since 'last' and upsert to vector DB
            # After successful run store new last_sync timestamp
            logger.info("Incremental load completed")
            finished_at = datetime.now(timezone.utc).isoformat()
            return {
                "status": "success",
                "message": f"Incremental load completed since {last}",
                "started_at": started_at,
                "finished_at": finished_at
            }
        except Exception as ex:
            logger.exception("IncrementalLoadStrategy.sync failed")
            finished_at = datetime.now(timezone.utc).isoformat()
            return {
                "status": "failure",
                "message": f"Exception: {ex}",
                "started_at": started_at,
                "finished_at": finished_at
            }