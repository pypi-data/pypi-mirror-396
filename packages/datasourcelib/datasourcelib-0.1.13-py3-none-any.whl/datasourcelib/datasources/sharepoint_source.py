from typing import Any, Dict, List, Optional, Tuple
from datasourcelib.datasources.datasource_base import DataSourceBase
from datasourcelib.utils.logger import get_logger
from datasourcelib.utils.validators import require_keys
from datasourcelib.utils.byte_reader import ByteReader
import requests
import pandas as pd
import os
from uuid import uuid4
from datetime import datetime, timedelta

logger = get_logger(__name__)
reader = ByteReader()


class SharePointSource(DataSourceBase):
    """
    SharePoint source using Microsoft Graph API with two App Registrations:
      - sp_master_config: client with Sites.Read.All (used to resolve site & drive)
      - sp_client_config: client with Site.Selected (used to download files)

    Config keys expected:
      sp_site_url: str
      sp_site_display_name: str
      sp_master_config: {sp_client_id, sp_client_secret, sp_tenant_id}
      sp_client_config: {sp_client_id, sp_client_secret}
      sp_pull_sub_items_enabled: bool | "true"/"false"
      sp_pull_sub_items_enabled_save_path: optional local folder
      sp_list_columns_to_keep: optional list[str] to filter list columns
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self._master_token: Optional[str] = None
        self._access_token: Optional[str] = None
        self._list_token: Optional[str] = None
        self._site_url: Optional[str] = None
        self._site_id: Optional[str] = None
        self._drive_id: Optional[str] = None

    # -------------------------
    # Connect / token helpers
    # -------------------------
    def validate_config(self) -> bool:
        try:
            require_keys(self.config, ["sp_site_url", "sp_master_config", "sp_client_config", "sp_site_display_name"])
            return True
        except Exception as ex:
            logger.error("SharePointSource.validate_config: %s", ex)
            return False

    def _get_token(self, client_id: str, client_secret: str, tenant_id: str) -> str:
        token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
        payload = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": "https://graph.microsoft.com/.default",
        }
        resp = requests.post(token_url, data=payload, timeout=30)
        resp.raise_for_status()
        token = resp.json().get("access_token")
        if not token:
            logger.info("$$$ - Token response missing access_token  -$$$")
        return token

    def _get_list_token(self, client_id: str, client_secret: str, tenant_id: str, domain_name: str) -> str:
        """
        Get SharePoint-specific access token for list operations using legacy endpoint.
        This token is different from Graph API token and is used specifically for SharePoint REST API calls.
        """
        try:
            list_site_url = f"https://accounts.accesscontrol.windows.net/{tenant_id}/tokens/OAuth/2"
            
            # Format client_id with tenant and construct resource string for SharePoint
            list_credentials = {
                'grant_type': 'client_credentials',
                'client_id': f"{client_id}@{tenant_id}",
                'client_secret': client_secret,
                'resource': f"00000003-0000-0ff1-ce00-000000000000/{domain_name}.sharepoint.com@{tenant_id}"
            }
            
            response = requests.post(list_site_url, data=list_credentials, timeout=30)
            response.raise_for_status()
            
            token = response.json().get("access_token")
            if not token:
                logger.info("$$$ - SharePoint list token response missing access_token -$$$")
                
            return token
        
        except Exception as ex:
            logger.info("$$$ - Failed to obtain SharePoint list token -$$$")

    def _resolve_site_and_drive(self, site_display_name: str) -> None:
        if not self._master_token:
            raise RuntimeError("master token missing")
        # Resolve site id
        find_site_id_url = f"https://graph.microsoft.com/v1.0/sites?search={site_display_name}"
        resp = requests.get(find_site_id_url, headers={"Authorization": f"Bearer {self._master_token}"}, timeout=30)
        resp.raise_for_status()
        items = resp.json().get("value", [])
        if not items:
            raise RuntimeError("site not found for display name: " + site_display_name)
        self._site_id = items[0].get("id")
        logger.info("Resolved SharePoint site ID: %s", self._site_id)

        # Resolve drive id
        drive_url = f"https://graph.microsoft.com/v1.0/sites/{self._site_id}/drives"
        resp = requests.get(drive_url, headers={"Authorization": f"Bearer {self._master_token}"}, timeout=30)
        resp.raise_for_status()
        drives = resp.json().get("value", [])
        if not drives:
            raise RuntimeError("no drives found for site id: " + str(self._site_id))
        self._drive_id = drives[0].get("id")
        logger.info("Resolved SharePoint drive ID: %s", self._drive_id)

    def _get_client_credentials(self) -> Tuple[str, str]:
        """Retrieve client credentials in order of priority: sp_download_config, sp_client_config, sp_master_config."""
        # Fallback to sp_client_config
        sp_client_config = self.config.get("sp_client_config", {})
        client_id = sp_client_config.get("sp_client_id")
        client_secret = sp_client_config.get("sp_client_secret")

        if not client_id or not client_secret:
            # Fallback to sp_master_config
            sp_master_config = self.config.get("sp_master_config", {})
            client_id = client_id or sp_master_config.get("sp_client_id")
            client_secret = client_secret or sp_master_config.get("sp_client_secret")

        if not client_id or not client_secret:
            raise ValueError("Client ID and Client Secret must be provided in the configuration.")

        return client_id, client_secret

    def _get_download_credentials(self) -> Tuple[str, str]:
        """Retrieve client credentials in order of priority: sp_download_config, sp_client_config, sp_master_config."""
        # Check sp_download_config first
        sp_download_config = self.config.get("sp_client_config", {}).get("sp_download_config", {})
        client_id = sp_download_config.get("sp_client_id")
        client_secret = sp_download_config.get("sp_client_secret")

        if not client_id or not client_secret:
            # Fallback to sp_client_config
            sp_client_config = self.config.get("sp_client_config", {})
            client_id = client_id or sp_client_config.get("sp_client_id")
            client_secret = client_secret or sp_client_config.get("sp_client_secret")

            if not client_id or not client_secret:
                # Fallback to sp_master_config
                sp_master_config = self.config.get("sp_master_config", {})
                client_id = client_id or sp_master_config.get("sp_client_id")
                client_secret = client_secret or sp_master_config.get("sp_client_secret")

        if not client_id or not client_secret:
            raise ValueError("Client ID and Client Secret must be provided in the configuration.")

        return client_id, client_secret


    def connect(self) -> bool:
        try:
            # basic values
            self._site_url = self.config["sp_site_url"]
            master_config = self.config["sp_master_config"]

            # get master token (Sites.Read.All)
            try:
                master_client_id = master_config["sp_client_id"]
                master_client_secret = master_config["sp_client_secret"]
                self._master_token = self._get_token(master_client_id, master_client_secret, master_config["sp_tenant_id"])
                logger.info("$$$ - Obtained master access token for SharePoint - $$$")
            except Exception as ex:
                logger.info("$$$ - Failed to obtain master token - $$$")

            # resolve site and drive ids
            try:
                self._resolve_site_and_drive(self.config['sp_site_display_name'])
            except Exception:
                logger.info("$$$ - Failed to resolve site/drive - $$$")

            # get client token (Site.Selected) for download operations
            try:
                client_id, client_secret = self._get_client_credentials()
                self._access_token = self._get_token(client_id, client_secret, master_config["sp_tenant_id"])
                logger.info("$$$ - Obtained client access token for SharePoint downloads - $$$")
            except Exception:
                logger.info("$$$ - Failed to obtain client access token - $$$")

            # get list client token (Site.Selected) for list operations
            try:
                client_id, client_secret = self._get_client_credentials()
                self._list_token = self._get_list_token(client_id, client_secret, master_config["sp_tenant_id"], master_config["sp_domain_name"])
                logger.info("$$$ - Obtained client list token for SharePoint list operations - $$$")
            except Exception:
                logger.info("$$$ - Failed to obtain client list token - $$$")

            self._connected = True
            logger.info("SharePointSource connected for site: %s", self._site_url)
            return True

        except Exception as ex:
            logger.exception("SharePointSource.connect failed")
            self._connected = False
            return False

    def disconnect(self) -> None:
        self._connected = False
        self._master_token = None
        self._access_token = None
        self._site_id = None
        self._drive_id = None
        logger.info("SharePointSource disconnected")

    # -------------------------
    # Download / extraction helpers
    # -------------------------
    def _download_file_bytes(self, relative_path: str) -> Tuple[bytes, str]:
        """Download file bytes via Graph content endpoint. Returns (bytes, filename)."""
        if not (self._site_id and self._drive_id and self._access_token):
            raise RuntimeError("site/drive/token not resolved")
        file_url = f"https://graph.microsoft.com/v1.0/sites/{self._site_id}/drives/{self._drive_id}/root:/{relative_path}:/content"
        headers = {"Authorization": f"Bearer {self._access_token}"}
        resp = requests.get(file_url, headers=headers, timeout=60)
        resp.raise_for_status()
        filename = os.path.basename(relative_path)
        return resp.content, filename

    def _extract_table_rows(self, content: bytes, filename: str) -> List[Dict[str, Any]]:
        """Normalize CSV/XLSX/TSV bytes into list[dict]."""
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        # If it's a known table format, use ByteReader to get a table object
        if ext in ("csv", "xlsx", "xls", "tsv"):
            table = reader.read_table_from_bytes(content, ext=ext)
            # Normalize shapes to list[dict]
            if hasattr(table, "to_dict"):
                rows = table.to_dict(orient="records")
            elif hasattr(table, "to_pandas"):
                rows = table.to_pandas().to_dict(orient="records")
            elif isinstance(table, list) and table and isinstance(table[0], dict):
                rows = table
            elif isinstance(table, list) and table and isinstance(table[0], (list, tuple)):
                cols = getattr(table, "columns", None)
                if not cols and all(isinstance(x, str) for x in table[0]):
                    cols = table[0]
                    data_rows = table[1:]
                else:
                    data_rows = table
                if not cols and data_rows:
                    cols = [f"col{i}" for i in range(len(data_rows[0]))]
                rows = [dict(zip(cols, r)) for r in data_rows]
            else:
                vals = getattr(table, "values", None)
                if vals is not None:
                    try:
                        rows_list = vals.tolist()
                    except Exception:
                        rows_list = list(vals)
                    cols = list(getattr(table, "columns", [])) or [f"col{i}" for i in range(len(rows_list[0]) if rows_list else 0)]
                    rows = [{cols[i]: r[i] for i in range(len(cols))} for r in rows_list]
                else:
                    rows = [{"content": str(table)}]
            # attach metadata
            for r in rows:
                r.setdefault("reference_name", filename)
                r.setdefault("reference_size", len(content))
            return rows
        else:
            # not a table format: return text content
            text = reader.read_text_from_bytes(content, ext=ext)
            return [{"name": filename, "content": text, "size": len(content)}]

    def _save_file_if_requested(self, content: bytes, filename: str, save_path: Optional[str]) -> Optional[str]:
        if not save_path:
            return None
        os.makedirs(save_path, exist_ok=True)
        outpath = os.path.join(save_path, filename) if os.path.isdir(save_path) else save_path
        with open(outpath, "wb") as fh:
            fh.write(content)
        logger.info("Saved downloaded file to %s", outpath)
        return outpath

    # -------------------------
    # REST / List helpers
    # -------------------------
    def _fetch_list_items_via_rest(self, relative_api_path: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Call SharePoint REST API (_api/...) using master token and return cleaned dataframe rows."""
        if not self._master_token:
            raise RuntimeError("master token missing")
        url = f"{self._site_url.rstrip('/')}/{relative_api_path.lstrip('/')}"
        headers = {"Authorization": f"Bearer {self._list_token}", "Accept": "application/json;odata=verbose"}
        resp = requests.get(url, headers=headers, params=params, timeout=30)
        resp.raise_for_status()
        response_json = resp.json()
        if "d" in response_json and "results" in response_json["d"]:
            items = response_json["d"]["results"]
        elif "value" in response_json:
            items = response_json["value"]
        else:
            items = []
        if not items:
            return []
        df = pd.DataFrame(items)
        # filter columns if configured
        keep = self.config.get("sp_list_columns_to_keep")
        if isinstance(keep, list) and keep:
            cols_to_keep = [c for c in df.columns if c in keep]
        else:
            # exclude SharePoint metadata columns (start with '__' or prefixed with '@')
            cols_to_keep = [c for c in df.columns if not str(c).startswith("__") and not str(c).startswith("@")]
        df = df[cols_to_keep]
        results = df.to_dict("records")
        for row in results:
            row.setdefault("reference_list_name", relative_api_path)
            row.setdefault("reference_site_url", self._site_url)
        return results

    # -------------------------
    # Public fetch_data (uses helpers)
    # -------------------------
    def fetch_data(self, query: Optional[str] = None, **kwargs) -> List[Dict[str, Any]]:
        """
        High-level fetch:
          - If sp_pull_sub_items_enabled==True (or kwargs sp_pull_sub_items_enabled) -> download file and return rows/content
          - If relative path starts with '_api/' -> call SharePoint REST and return list rows
          - Otherwise list folder children via Graph drives API
        """
        if not self._connected:
            if not self.connect():
                raise RuntimeError("Cannot connect to SharePoint")

        relative_path = query or self.config.get("sp_relative_path")
        if not relative_path:
            raise ValueError("No path specified")

        # interpret sp_pull_sub_items_enabled flags (allow "true"/"false" strings)
        sp_pull_sub_items_enabled_cfg = kwargs.get("sp_pull_sub_items_enabled", self.config.get("sp_pull_sub_items_enabled", False))
        sp_pull_sub_items_enabled = (str(sp_pull_sub_items_enabled_cfg).lower() == "true") if isinstance(sp_pull_sub_items_enabled_cfg, str) else bool(sp_pull_sub_items_enabled_cfg)
        save_path = kwargs.get("save_to") or self.config.get("sp_pull_sub_items_enabled_save_path")

        if not sp_pull_sub_items_enabled and not str(relative_path).startswith("_api/"):
            # download flow
            content, filename = self._download_file_bytes(relative_path)
            # optionally save raw file
            saved = self._save_file_if_requested(content, filename, save_path)
            rows = self._extract_table_rows(content, filename)
            # attach url metadata
            for r in rows:
                r.setdefault("reference_source_url", f"graph:/sites/{self._site_id}/drives/{self._drive_id}/root:/{relative_path}:")
                if saved:
                    r.setdefault("saved_to", saved)
            return rows

        # non-download flows
        try:
            if str(relative_path).startswith("_api/"):
                params = kwargs.get("params")
                #return self._fetch_list_items_via_rest(relative_path, params=params)
                if sp_pull_sub_items_enabled:
                    # download individual items
                    results = []
                    items = self._fetch_list_items_via_rest(relative_path)

                    client_id, client_secret = self._get_download_credentials()

                    self._access_token = self._get_token(client_id, client_secret, self.config.get("sp_master_config",{})["sp_tenant_id"])
                    #test running with hardcoded items
                    if False:
                        items = []
                        # obtain access token for download if not already done
                        
                        items.append({
                            "Title": "Enterprise Knowledge Hub Agent - User Guide",
                            "SiteDisplayName": "Barrick Global Data Platform - Governance Forum",
                            "RelativePath": "/10. Shared Documents/Environment/Infrastructure/Enterprise Knowledge Hub Agent - User Guide.docx"
                        })
                        items.append({
                            "Title": "Halo - Everything you need to know about AI",
                            "SiteDisplayName": "Barrick Global Data Platform - Governance Forum",
                            "RelativePath": "/10. Shared Documents/Environment/Infrastructure/Halo - Everything you need to know about AI.pdf"
                        })
                        items.append({
                            "Title": "Power_Platform_CoPilot_Deck",
                            "SiteDisplayName": "Barrick Global Data Platform - Governance Forum",
                            "RelativePath": "/10. Shared Documents/Environment/Infrastructure/Power_Platform_CoPilot_Deck.pptx"
                        })

                    for item in items:
                        #the path after [Shared Documents/] in relative path                      
                        item_relative_path = item.get("RelativePath") or item.get("relativepath") or item.get("relativePath")
                        item_name = item.get("Title") or item.get("title")
                        item_display_name = item.get("SiteDisplayName") or item.get("sitedisplayname") or item.get("siteDisplayName")
                        
                        # Check ModifiedDate filter 
                        # "2024-01-15" → 10 chars || "20240115" → 8 chars
                        modified_date_str = item.get("ModifiedDate") or item.get("modifieddate") or item.get("modifiedDate")
                        if modified_date_str:
                            try:
                                modified_date = datetime.fromisoformat(modified_date_str.replace('Z', '+00:00'))
                                if datetime.now(modified_date.tzinfo) - modified_date < timedelta(days=1):
                                    continue
                            except Exception:
                                pass
                        
                        if not item_relative_path:
                            logger.warning("Item missing RelativePath: %s", item)
                            continue

                        #get site id and drive id for this item
                        self._resolve_site_and_drive(item_display_name)  
 
                        try:
                            content, filename = self._download_file_bytes(item_relative_path)
                            saved = self._save_file_if_requested(content, filename, save_path)
                            extracted_rows = self._extract_table_rows(content, filename)
                            for r in extracted_rows:
                                r.update(item)  # merge metadata
                                r.setdefault("reference_source_url", f"graph:/sites/{self._site_id}/drives/{self._drive_id}/root:/{item_relative_path}:")
                                if saved:
                                    r.setdefault("saved_to", saved)
                            results.extend(extracted_rows)
                        except Exception:
                            logger.exception("Failed to download/extract item: %s", item_relative_path)
                    return results
                else:
                    return self._fetch_list_items_via_rest(relative_path, params=params)
            else:
                # folder listing via Graph
                folder_url = f"https://graph.microsoft.com/v1.0/sites/{self._site_id}/drives/{self._drive_id}/root:/{relative_path}:/children"
                resp = requests.get(folder_url, headers={"Authorization": f"Bearer {self._access_token}"}, timeout=30)
                resp.raise_for_status()
                items = resp.json().get("value", [])
                results = []
                for item in items:
                    results.append({
                        "name": item.get("name"),
                        "url": item.get("webUrl"),
                        "size": item.get("size"),
                        "created": item.get("createdDateTime"),
                        "modified": item.get("lastModifiedDateTime")
                    })
                return results
        except Exception:
            logger.exception("Failed to fetch SharePoint data")
            raise