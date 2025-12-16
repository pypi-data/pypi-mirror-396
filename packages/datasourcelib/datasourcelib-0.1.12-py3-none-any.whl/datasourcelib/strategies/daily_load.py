from datasourcelib.core.sync_base import SyncBase
from datasourcelib.utils.logger import get_logger
from datetime import datetime, timezone
from typing import Dict, Any, Optional

logger = get_logger(__name__)

class DailyLoadStrategy(SyncBase):
    """Daily scheduled load strategy (wraps incremental sync)."""

    def validate(self) -> bool:
        """Validate strategy preconditions."""
        return True

    def sync(self, run_date: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Execute daily load for the given run_date (ISO date string).
        If run_date is None, today's UTC date is used.

        Returns a dict with status, message and ISO timestamps.
        """
        # Ensure run_date and started_at exist even if exceptions occur early
        run_date = run_date
        started_at = datetime.now(timezone.utc).isoformat()
        try:
            run_date = run_date or datetime.now(timezone.utc).date().isoformat()
            logger.info("Starting daily load for %s (requested run_date=%s)", started_at, run_date)

            # TODO: call incremental sync / processing here, for example:
            # result = self.incremental_sync(last_sync=..., **kwargs)

            finished_at = datetime.now(timezone.utc).isoformat()
            return {
                "status": "success",
                "message": f"Daily load completed for {run_date}",
                "started_at": started_at,
                "finished_at": finished_at
            }
        except Exception as ex:
            logger.exception("DailyLoadStrategy.sync failed")
            finished_at = datetime.now(timezone.utc).isoformat()
            return {
                "status": "failure",
                "message": f"Exception: {ex}",
                "started_at": started_at,
                "finished_at": finished_at
            }