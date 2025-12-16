from abc import ABC, abstractmethod
from typing import Any, Dict
from datasourcelib.datasources.datasource_base import DataSourceBase

class SyncBase(ABC):
    """Base class for all sync strategies."""

    def __init__(self, data_source: DataSourceBase, vector_db_config: Dict[str, Any]):
        self.vector_db_config = vector_db_config
        self.data_source = data_source
    @abstractmethod
    def validate(self) -> bool:
        """Validate strategy configuration before running."""
        raise NotImplementedError

    @abstractmethod
    def sync(self, **kwargs) -> Dict[str, Any]:
        """Execute sync operation. Returns True on success, False otherwise."""
        raise NotImplementedError