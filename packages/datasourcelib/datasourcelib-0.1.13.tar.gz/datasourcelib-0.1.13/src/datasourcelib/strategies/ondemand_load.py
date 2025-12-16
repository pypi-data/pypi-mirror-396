from datasourcelib.core.sync_base import SyncBase
from datasourcelib.utils.logger import get_logger
from typing import Dict, Any
from datetime import datetime, timezone
logger = get_logger(__name__)

class OnDemandLoadStrategy(SyncBase):
    """On demand load triggered by user request (arbitrary params)."""

    def validate(self) -> bool:
        return True

    def sync(self, **kwargs) -> Dict[str, Any]:
        try:
            started_at = datetime.now(timezone.utc).isoformat()
            logger.info("On-demand sync invoked with params: %s", kwargs)
            # Use kwargs to drive partial loads, filters, ids etc.
            finished_at = datetime.now(timezone.utc).isoformat()
            return {
                "status": "success",
                "message": f"Ondemand load completed.",
                "started_at": started_at,
                "finished_at": finished_at
            }
        except Exception as ex:
            logger.exception("OnDemandLoadStrategy.sync failed")
            finished_at = datetime.now(timezone.utc).isoformat()
            return {
                "status": "failure",
                "message": f"Exception: {ex}",
                "started_at": started_at,
                "finished_at": finished_at
            }