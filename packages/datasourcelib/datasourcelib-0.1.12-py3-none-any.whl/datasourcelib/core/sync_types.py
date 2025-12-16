from enum import Enum

class SyncType(str, Enum):
    FULL = "full"
    INCREMENTAL = "incremental"
    TIMERANGE = "timerange"
    DAILY = "daily"
    ONDEMAND = "ondemand"

class SyncStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    IN_PROGRESS = "in_progress"

