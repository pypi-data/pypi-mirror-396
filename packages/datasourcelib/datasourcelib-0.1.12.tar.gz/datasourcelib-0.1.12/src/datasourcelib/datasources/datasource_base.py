from abc import ABC, abstractmethod
from typing import Any, Dict, List

class DataSourceBase(ABC):
    """
    Abstract base for all data sources.
    Concrete implementations should implement config validation, connect/disconnect and a fetch_data method.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config or {}
        self._connected = False

    @abstractmethod
    def validate_config(self) -> bool:
        """Validate the configuration dict for required keys."""
        raise NotImplementedError

    @abstractmethod
    def connect(self) -> bool:
        """Establish connection to the data source. Returns True on success."""
        raise NotImplementedError

    @abstractmethod
    def disconnect(self) -> None:
        """Close any open connections / cleanup."""
        raise NotImplementedError

    @abstractmethod
    def fetch_data(self, query: str = None, **kwargs) -> List[Dict[str, Any]]:
        """Fetch rows from the source (list of dicts)."""
        raise NotImplementedError