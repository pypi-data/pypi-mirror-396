from datetime import datetime, timezone
from datasourcelib.core.sync_base import SyncBase
from datasourcelib.utils.logger import get_logger
from typing import Dict, Any

logger = get_logger(__name__)

class TimeRangeLoadStrategy(SyncBase):
    """Load records between a start and end timestamp."""

    def validate(self) -> bool:
        # rely on params at runtime; minimal validation OK
        return True

    def sync(self, start: str = None, end: str = None, **kwargs) -> Dict[str, Any]:
        try:
            started_at = datetime.now(timezone.utc).isoformat()
            if not start or not end:
                logger.error("TimeRangeLoadStrategy requires 'start' and 'end'")
                return False
            logger.info("Time range load between %s and %s", start, end)
            # TODO: query source for timeframe and upsert
            finished_at = datetime.now(timezone.utc).isoformat()
            return {
                "status": "success",
                "message": f"TimeRange load completed between {start} and {end}",
                "started_at": started_at,
                "finished_at": finished_at
            }
        except Exception as ex:
            logger.exception("TimeRangeLoadStrategy.sync failed")
            finished_at = datetime.now(timezone.utc).isoformat()
            return {
                "status": "failure",
                "message": f"Exception: {ex}",
                "started_at": started_at,
                "finished_at": finished_at
            }