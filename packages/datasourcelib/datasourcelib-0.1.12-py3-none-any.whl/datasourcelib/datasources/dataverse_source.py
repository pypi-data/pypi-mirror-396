from typing import Any, Dict, List, Optional, Tuple
from datasourcelib.datasources.datasource_base import DataSourceBase
from datasourcelib.utils.logger import get_logger
from datasourcelib.utils.validators import require_keys
from datasourcelib.utils.aggregation import generate_grouped_summaries
from azure.identity import DefaultAzureCredential
import pyodbc
import time
import pandas as pd

# optional requests import (webapi mode)
try:
    import requests  # type: ignore
except Exception:
    requests = None  # lazy import

logger = get_logger(__name__)

class DataverseSource(DataSourceBase):
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self._conn = None
        self._mode = (self.config.get("dv_mode") or "tds").lower()  # "tds" or "webapi"
        self._access_token: Optional[str] = None
        self._headers: Dict[str, str] = {}
        self._max_retries = int(self.config.get("dv_max_retries", 3))

    def validate_config(self) -> bool:

        """
        Validate required keys depending on selected dv_mode.
        - tds: requires either 'tds_connection_string' OR ('dataverse_server' and 'dataverse_database')
        - webapi: 
            * client credentials: 'dv_webapi_url','dv_webapi_client_id','dv_webapi_client_secret','dv_webapi_tenant_id'
            * managed identity:    'dv_webapi_url' + dv_webapi_managed_identity_auth=True
        """

        try:            
            if self._mode == "webapi":
                use_mi = bool(self.config.get("dv_webapi_managed_identity_auth", False))
                require_keys(self.config, ["dv_webapi_url"])
                if not use_mi:
                    require_keys(
                        self.config,
                        ["dv_webapi_client_id", "dv_webapi_client_secret", "dv_webapi_tenant_id"]
                    )
                return True

            if self._mode == "webapi":
                require_keys(self.config, ["dv_webapi_url", "dv_webapi_client_id", "dv_webapi_client_secret", "dv_webapi_tenant_id"])
            else:
                # TDS mode (ODBC)
                if "dv_tds_connection_string" in self.config:
                    return True
                # otherwise require components
                require_keys(self.config, ["dv_tds_server", "dv_tds_database"])
                # if not using integrated auth require creds
                if not bool(self.config.get("dv_tds_windows_auth", False)):
                    require_keys(self.config, ["dv_tds_username", "dv_tds_password"])
            return True
        except Exception as ex:
            logger.error("DataverseSource.validate_config failed: %s", ex)
            return False

    # -------------------------
    # Connection helpers
    # -------------------------
    def _get_available_driver(self) -> str:
        """Return first suitable ODBC driver for SQL/Dataverse TDS access."""
        preferred_drivers = [
            "ODBC Driver 18 for SQL Server",
            "ODBC Driver 17 for SQL Server",
            "SQL Server Native Client 11.0",
            "SQL Server"
        ]
        try:
            drivers = pyodbc.drivers()
            logger.info("Available ODBC drivers: %s", drivers)
            
            for d in preferred_drivers:
                if d in drivers:
                    logger.info("Using ODBC driver: %s", d)
                    return d
            
            # fallback to first available
            if drivers:
                logger.warning("No preferred driver found. Using: %s", drivers[0])
                return drivers[0]
            raise RuntimeError("No ODBC drivers available")
        except Exception as ex:
            logger.error("DataverseSource._get_available_driver failed: %s", ex)
            raise

    def _build_tds_conn_str(self) -> str:
        """Build valid connection string with proper parameter names."""
        if "dv_tds_connection_string" in self.config:
            return self.config["dv_tds_connection_string"]
        
        driver = self._get_available_driver()
        # Fix: use correct config key names (dv_tds_server, not dv_tds_dataverse_server)
        server = self.config.get("dv_tds_server", "").strip()
        database = self.config.get("dv_tds_database", "").strip()
        
        if not server:
            raise ValueError("dv_tds_server are required")
        
        logger.info("Building TDS connection (driver=%s, server=%s, database=%s)", driver, server, database)
        
        # Use curly braces for driver name (handles spaces in driver names)
        parts = [f"DRIVER={{{driver}}}"]
        parts.append(f"Server={server}")
        parts.append(f"Database={database}")
        password = None
        if bool(self.config.get("dv_tds_windows_auth", False)):
            parts.append("Trusted_Connection=yes")
            logger.info("Using Windows authentication")
        else:
            username = self.config.get("dv_tds_username", "").strip()
            password = self.config.get("dv_tds_password", "").strip()
            
            if not username or not password:
                raise ValueError("dv_tds_username and dv_tds_password required when Windows auth disabled")
            
            parts.append(f"UID={username}")
            parts.append(f"PWD={password}")
            parts.append("Authentication=ActiveDirectoryInteractive")
        # Encryption settings
        if not bool(self.config.get("dv_tds_is_onprem", False)):
            parts.append("Encrypt=yes")
            parts.append("TrustServerCertificate=no")
        else:
            parts.append("Encrypt=optional")
            parts.append("TrustServerCertificate=yes")
        
        conn_str = ";".join(parts)
        logger.debug("Connection string: %s", conn_str.replace(password or "", "***") if password else conn_str)
        return conn_str

    def _obtain_webapi_token(self) -> Tuple[str, Dict[str, str]]:

        """
        Acquire OAuth2 token for Dataverse Web API.
        Returns (access_token, headers)

        Paths:
            - Managed Identity (dv_webapi_managed_identity_auth=True): uses DefaultAzureCredential and scope '<webapi_url>/.default'
            - Client Credentials (dv_webapi_managed_identity_auth=False): uses OAuth2 client credentials with tenant/client/secret
        """

        webapi_url = self.config["dv_webapi_url"].rstrip("/")
        # Scope for MSAL-style request
        scope = f"{webapi_url}/.default"

        use_mi = bool(self.config.get("dv_webapi_managed_identity_auth", False))

        # --- Managed Identity / DefaultAzureCredential path ---
        if use_mi:
            if DefaultAzureCredential is None:
                raise RuntimeError(
                    "azure-identity package required for managed identity auth (pip install azure-identity)"
                )
            # DefaultAzureCredential works with system/user-assigned MI in Azure,
            # and falls back to developer credentials locally (Azure CLI/VS Code).
            credential = DefaultAzureCredential()
            # Obtain token for Dataverse scope
            token_obj = credential.get_token(scope)
            token = token_obj.token
            if not token:
                raise RuntimeError("Failed to obtain Managed Identity token for Dataverse Web API")
            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/json",
                "OData-MaxVersion": "4.0",
                "OData-Version": "4.0"
            }
            return token, headers

        if requests is None:
            raise RuntimeError("requests package required for Dataverse Web API mode")
        tenant = self.config["dv_webapi_tenant_id"]
        client_id = self.config["dv_webapi_client_id"]
        client_secret = self.config["dv_webapi_client_secret"]
        # resource or scope: prefer explicit resource, else fallback to webapi_url host
        resource = self.config.get("dv_webapi_resource")
        if not resource:
            # infer resource from webapi_url e.g. https://<org>.crm.dynamics.com
            webapi_url = self.config["dv_webapi_url"].rstrip("/")
            resource = webapi_url.split("://")[-1]
            resource = f"https://{resource}"  # as resource
        token_url = f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token"
        data = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": f"{resource}/.default"
        }
        resp = requests.post(token_url, data=data, timeout=30)
        resp.raise_for_status()
        j = resp.json()
        token = j.get("access_token")
        if not token:
            raise RuntimeError("Failed to obtain access token for Dataverse webapi")
        headers = {"Authorization": f"Bearer {token}", "Accept": "application/json", "OData-MaxVersion": "4.0", "OData-Version": "4.0"}
        return token, headers

    # -------------------------
    # Public connection API
    # -------------------------
    def connect(self) -> bool:
        try:
            if self._mode == "webapi":
                token, headers = self._obtain_webapi_token()
                self._access_token = token
                self._headers = headers
                self._connected = True
                
                auth_mode = "managed identity" if bool(self.config.get("dv_webapi_managed_identity_auth", False)) else "client credentials"
                logger.info("DataverseSource connected (webapi, %s) to %s", auth_mode, self.config.get("dv_webapi_url"))

                return True
            # else TDS mode
            conn_str = self._build_tds_conn_str()
            self._conn = pyodbc.connect(conn_str, timeout=int(self.config.get("dv_tds_timeout", 30)))
            self._connected = True
            logger.info("DataverseSource connected (dv_tds mode) to %s/%s", self.config.get("dv_server"), self.config.get("dv_database"))
            return True
        except pyodbc.Error as ex:
            logger.error("DataverseSource.connect failed - ODBC Error: %s", ex)
            self._connected = False
            return False
        except requests.RequestException as ex:
            logger.error("DataverseSource.connect failed - HTTP Error: %s", ex)
            self._connected = False
            return False
        except Exception as ex:
            logger.exception("DataverseSource.connect failed")
            self._connected = False
            return False

    def disconnect(self) -> None:
        try:
            if self._conn:
                try:
                    self._conn.close()
                except Exception:
                    pass
            self._conn = None
            self._access_token = None
            self._headers = {}
        finally:
            self._connected = False
            logger.info("DataverseSource disconnected")

    # -------------------------
    # Data fetch
    # -------------------------
    def fetch_data(self, query: Optional[str] = None, **kwargs) -> List[Dict[str, Any]]:
        """
        Fetch rows from Dataverse.
        - TDS mode: executes SQL query (config key 'tds_query' or provided 'query')
        - WebAPI mode: calls Dataverse Web API path fragment (e.g. 'accounts?$select=name') or uses 'entity_set' + query params
        Returns list[dict].
        """
        attempt = 0
        while attempt < self._max_retries:
            try:
                if not getattr(self, "_connected", False):
                    ok = self.connect()
                    if not ok:
                        raise RuntimeError("DataverseSource: cannot connect")

                if self._mode == "webapi":
                    if requests is None:
                        raise RuntimeError("requests package required for webapi mode")
                    webapi_url = self.config["dv_webapi_url"].rstrip("/")
                    # if query provided, treat it as path fragment; else use entity_set from config
                    path_fragment = query or self.config.get("dv_webapi_entity_set")
                    if not path_fragment:
                        raise ValueError("DataverseSource.fetch_data requires a webapi 'query' or 'entity_set' in config")
                    url = f"{webapi_url}/api/data/v9.1/{path_fragment.lstrip('/')}"
                    params = kwargs.get("params")
                    resp = requests.get(url, headers=self._headers, params=params, timeout=60)
                    resp.raise_for_status()
                    j = resp.json()
                    items: Any = []
                    # Dataverse OData responses typically use 'value' for collections
                    if isinstance(j, dict) and "value" in j:
                        items = j["value"]
                    # otherwise return the raw json wrapped in a list or as-is
                    elif isinstance(j, list):
                        items= j
                    else:
                        items= [j]

                    df = pd.DataFrame(items)
                    # filter columns if configured
                    keep = self.config.get("dv_webapi_columns_to_keep")
                    if isinstance(keep, list) and keep:
                        cols_to_keep = [c for c in df.columns if c in keep]
                    else:
                        # exclude SharePoint metadata columns (start with '__' or prefixed with '@')
                        cols_to_keep = [c for c in df.columns if not str(c).startswith("__") and not str(c).startswith("@")]
                    df = df[cols_to_keep]
                    summaries = generate_grouped_summaries(
                        df=df,
                        aggregation_field=self.config.get("dv_webapi_aggregation_field"),
                        row_format=self.config.get("dv_webapi_row_format"),
                        constants={"title": ""},
                        header_format=self.config.get("dv_webapi_header_format"),
                        sort_by=self.config.get("dv_webapi_sort_by"),     # or a column/list if you want ordering
                        validate=True     # ensures all placeholders exist
                    )
                    
                    return summaries
                    #results = df.to_dict("records")
                    #return results
                # else TDS mode
                sql = query or self.config.get("dv_tds_query") or self.config.get("dv_sql_query")
                if not sql:
                    raise ValueError("DataverseSource.fetch_data requires a SQL query (tds mode)")

                cur = self._conn.cursor()
                try:
                    cur.execute(sql)
                    cols = [c[0] for c in (cur.description or [])]
                    rows = cur.fetchall()
                    results: List[Dict[str, Any]] = []
                    for r in rows:
                        results.append({cols[i]: r[i] for i in range(len(cols))})
                    
                    df = pd.DataFrame(results)
                    summaries = generate_grouped_summaries(
                        df=df,
                        aggregation_field=self.config.get("dv_tds_aggregation_field"),
                        row_format=self.config.get("dv_tds_row_format"),
                        constants={"title": ""},
                        header_format=self.config.get("dv_tds_header_format"),
                        sort_by=self.config.get("dv_tds_sort_by"),     # or a column/list if you want ordering
                        validate=True     # ensures all placeholders exist
                    )
                    
                    return summaries
                finally:
                    try:
                        cur.close()
                    except Exception:
                        pass

            except Exception as ex:
                attempt += 1
                logger.warning("DataverseSource.fetch_data attempt %d/%d failed: %s", attempt, self._max_retries, ex)
                # transient retry for network/connection errors
                if attempt >= self._max_retries:
                    logger.exception("DataverseSource.fetch_data final failure")
                    raise
                # backoff
                time.sleep(min(2 ** attempt, 10))
                # try reconnect for next attempt
                try:
                    self.disconnect()
                except Exception:
                    pass

        # unreachable; defensive
        return []
