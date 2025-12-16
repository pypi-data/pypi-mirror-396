class DatasourceLibError(Exception):
    """Base exception for datasourcelib."""

class SyncStrategyNotFound(DatasourceLibError):
    """Raised when a strategy is not found."""

# Added: DataSourceNotFound to represent missing/unknown data sources
class DataSourceNotFound(DatasourceLibError):
    """Raised when a data source is not found or not registered."""