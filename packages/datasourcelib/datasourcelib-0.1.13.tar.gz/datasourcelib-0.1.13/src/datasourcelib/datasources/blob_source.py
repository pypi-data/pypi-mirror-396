from typing import Any, Dict, List, Optional
from datasourcelib.datasources.datasource_base import DataSourceBase
from datasourcelib.utils.logger import get_logger
from datasourcelib.utils.validators import require_keys

logger = get_logger(__name__)

try:
    from azure.storage.blob import BlobServiceClient  # type: ignore
except Exception:
    BlobServiceClient = None

class BlobStorageSource(DataSourceBase):
    """
    Minimal Azure Blob Storage source. Config example:
    {
      "connection_string": "<connection string>" OR "account_url" & "credential",
      "container": "mycontainer",
      "blob_prefix": "optional/prefix/"
    }
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self._client = None

    def validate_config(self) -> bool:
        try:
            require_keys(self.config, ["container"])
            if not (self.config.get("connection_string") or (self.config.get("account_url") and self.config.get("credential"))):
                raise KeyError("Missing connection_string or (account_url and credential)")
            return True
        except Exception as ex:
            logger.error("BlobStorageSource.validate_config: %s", ex)
            return False

    def connect(self) -> bool:
        if BlobServiceClient is None:
            raise RuntimeError("azure-storage-blob is required for BlobStorageSource")
        try:
            if "connection_string" in self.config:
                self._client = BlobServiceClient.from_connection_string(self.config["connection_string"])
            else:
                self._client = BlobServiceClient(account_url=self.config["account_url"], credential=self.config["credential"])
            self._connected = True
            logger.info("BlobStorageSource connected")
            return True
        except Exception as ex:
            logger.exception("BlobStorageSource.connect failed: %s", ex)
            self._connected = False
            return False

    def disconnect(self) -> None:
        self._client = None
        self._connected = False
        logger.info("BlobStorageSource disconnected")

    def fetch_data(self, query: Optional[str] = None, **kwargs) -> List[Dict[str, Any]]:
        """
        Returns list of blobs metadata or optionally blob content if 'download' param is True.
        params:
            blob_prefix: override config prefix
            download: bool
        """
        if not getattr(self, "_connected", False):
            ok = self.connect()
            if not ok:
                raise RuntimeError("BlobStorageSource: cannot connect")

        container = self.config["container"]
        prefix = kwargs.get("blob_prefix", self.config.get("blob_prefix", ""))
        download = kwargs.get("download", False)

        container_client = self._client.get_container_client(container)
        results = []
        for blob in container_client.list_blobs(name_starts_with=prefix):
            if download:
                blob_client = container_client.get_blob_client(blob)
                stream = blob_client.download_blob()
                content = stream.readall()
                results.append({"name": blob.name, "content": content})
            else:
                results.append({
                    "name": blob.name,
                    "size": getattr(blob, "size", None),
                    "last_modified": getattr(blob, "last_modified", None)
                })
        return results