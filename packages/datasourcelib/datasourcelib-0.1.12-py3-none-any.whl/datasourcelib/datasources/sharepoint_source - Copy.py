from typing import Any, Dict, List, Optional
from datasourcelib.datasources.datasource_base import DataSourceBase
from datasourcelib.utils.logger import get_logger
from datasourcelib.utils.validators import require_keys
from datasourcelib.utils.byte_reader import ByteReader
import requests
import pandas as pd

logger = get_logger(__name__)
reader = ByteReader()
class SharePointSource(DataSourceBase):
    """
    SharePoint source using Microsoft Graph API with separate App Registrations.
    
    Config examples:
    1) Client Credentials:
        {
            "sp_site_url": "https://yourtenant.sharepoint.com/sites/yoursite",
            "sp_master_config": {
                "sp_client_id": "your-master-client-id",
                "sp_client_secret": "your-master-client-secret",
                "sp_tenant_id": "your-tenant-id"
            },
            "sp_client_config": {
                "sp_client_id": "your-client-id",
                "sp_client_secret": "your-client-secret"
            },
            "sp_site_display_name": "Your Site Display Name",
            "sp_relative_path": "Shared Documents/folder/file.pdf",
            "sp_download": true,
            "sp_download_save_path": "C:/Downloads"
        }
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self._master_token = None
        self._list_token = None
        self._access_token = None
        self._site_url = None
        self._site_id = None
        self._drive_id = None
        self._ctx = None

    def validate_config(self) -> bool:
        try:
            require_keys(self.config, ["sp_site_url", "sp_master_config", "sp_client_config", "sp_site_display_name"])
            return True
        except Exception as ex:
            logger.error("SharePointSource.validate_config: %s", ex)
            return False

    def connect(self) -> bool:
        try:
            site_url = self.config["sp_site_url"]
            client_config = self.config["sp_client_config"]
            master_config = self.config["sp_master_config"]
            try:
                # Get master access token using App Registration 2 (Site.Read.All)                
                master_site_url = f"https://login.microsoftonline.com/{master_config['sp_tenant_id']}/oauth2/v2.0/token"
                master_credentials = {
                    'grant_type': 'client_credentials',
                    'client_id': master_config["sp_client_id"],
                    'client_secret': master_config["sp_client_secret"],
                    'scope': 'https://graph.microsoft.com/.default'
                }
                master_response = requests.post(master_site_url, data=master_credentials)
                master_response.raise_for_status()
                self._master_token = master_response.json().get("access_token")
                logger.info("Obtained master access token for SharePoint")
            except Exception as ex:
                logger.error(" $$$$$$  Failed to obtain master access token for sharepoint. $$$$ ")

            try:
                # Get access token to fatch sharepoint list items
                master_config = self.config["sp_master_config"]
                list_site_url = f"https://accounts.accesscontrol.windows.net/{master_config['sp_tenant_id']}/tokens/OAuth/2"
                
                list_credentials = {
                    'grant_type': 'client_credentials',
                    'client_id': f"{client_config['sp_client_id']}@{master_config['sp_tenant_id']}",
                    'client_secret': client_config["sp_client_secret"],
                    'resource': f"00000003-0000-0ff1-ce00-000000000000/{master_config['sp_domain_name']}.sharepoint.com@{master_config['sp_tenant_id']}"
                }
                
                list_response = requests.post(list_site_url, data=list_credentials)
                list_response.raise_for_status()
                self._list_token = list_response.json().get("access_token")
                logger.info("Obtained list access token for SharePoint")
            except Exception as ex:
                logger.error(" $$$$$$  Failed to obtain list access token for sharepoint. $$$$ ")

            try:
                # Get site ID using Microsoft Graph API
                find_site_id_url = f"https://graph.microsoft.com/v1.0/sites?search={self.config['sp_site_display_name']}"
                site_id_response = requests.get(find_site_id_url, headers={"Authorization": f"Bearer {self._master_token}"})
                site_id_response.raise_for_status()
                self._site_id = site_id_response.json()['value'][0]['id']
                logger.info("Resolved SharePoint site ID: %s", self._site_id)

                # Get drive ID based on site ID
                drive_url = f"https://graph.microsoft.com/v1.0/sites/{self._site_id}/drives"
                drive_response = requests.get(drive_url, headers={"Authorization": f"Bearer {self._master_token}"})
                drive_response.raise_for_status()
                self._drive_id = drive_response.json()['value'][0]['id']
                logger.info("Resolved SharePoint drive ID: %s", self._drive_id)
            except Exception as ex:
                logger.error(" $$$$$$  Failed to resolve site or drive ID. Check site display name. $$$$ ")

            try:
                # Get access token using App Registration 1 (Site.Selected)
                client_site_url = f"https://login.microsoftonline.com/{master_config['sp_tenant_id']}/oauth2/v2.0/token"
                client_credentials = {
                    'grant_type': 'client_credentials',
                    'client_id': client_config["sp_client_id"],
                    'client_secret': client_config["sp_client_secret"],
                    'scope': 'https://graph.microsoft.com/.default'
                }
                client_response = requests.post(client_site_url, data=client_credentials)
                client_response.raise_for_status()
                access_token = client_response.json().get("access_token")
                logger.info("Obtained access token for downloading files")
            except Exception as ex:
                logger.error(" $$$$$$  Failed to obtain file download access token for sharepoint. $$$$ ")
            # store access token (do not use ClientContext here)
            self._access_token = access_token
            self._site_url = site_url

            self._connected = True
            logger.info("Connected to SharePoint site: %s", site_url)
            return True
        except Exception as ex:
            logger.exception("SharePointSource.connect failed")
            self._connected = False
            return False

    def disconnect(self) -> None:
        try:
            if self._ctx:
                self._ctx = None
        finally:
            self._connected = False
            logger.info("SharePointSource disconnected")

    def fetch_data(self, query: Optional[str] = None, **kwargs) -> List[Dict[str, Any]]:
        """
        Fetch data from SharePoint:
        - If sp_download=True: downloads file(s) from the specified path
        - Otherwise: retrieves list items or folder contents
        """
        if not self._connected:
            ok = self.connect()
            if not ok:
                raise RuntimeError("Cannot connect to SharePoint")

        try:
            relative_path = query or self.config.get("sp_relative_path")
            if not relative_path:
                raise ValueError("No path specified")

            sp_download = self.config.get("sp_download")
            logger.info(" -#- SharePointSource.fetch_data: sp_download=%s, path=%s , url=%s", sp_download, relative_path, self._site_url)
            save_path = kwargs.get("save_to") or self.config.get("sp_download_save_path")

            if sp_download.lower() == "true":
                # Handle file download
                try:
                    file_url = f"https://graph.microsoft.com/v1.0/sites/{self._site_id}/drives/{self._drive_id}/root:/{relative_path}:/content"
                    headers = {"Authorization": f"Bearer {self._access_token}"}
                    file_response = requests.get(file_url, headers=headers)
                    file_response.raise_for_status()

                    content = file_response.content
                    result = []
                    filename = relative_path.split("/")[-1]
                    ext = filename.rsplit(".", 1)[-1].lower()

                    if ext in ("csv", "xlsx", "xls"):
                        content_table = reader.read_table_from_bytes(content, ext=ext)

                        # Normalize content_table -> rows: List[Dict[str, Any]]
                        try:
                            # pandas DataFrame or DataFrame-like with to_dict
                            if hasattr(content_table, "to_dict"):
                                rows = content_table.to_dict(orient="records")
                            # pyarrow Table
                            elif hasattr(content_table, "to_pandas"):
                                rows = content_table.to_pandas().to_dict(orient="records")
                            # list of dicts already
                            elif isinstance(content_table, list) and content_table and isinstance(content_table[0], dict):
                                rows = content_table
                            # list of rows (list of lists/tuples) + optional 'columns' attr
                            elif isinstance(content_table, list) and content_table and isinstance(content_table[0], (list, tuple)):
                                cols = getattr(content_table, "columns", None)
                                # if first row looks like header strings, use it as columns
                                if not cols and all(isinstance(x, str) for x in content_table[0]):
                                    cols = content_table[0]
                                    data_rows = content_table[1:]
                                else:
                                    data_rows = content_table
                                if not cols and data_rows:
                                    cols = [f"col{i}" for i in range(len(data_rows[0]))]
                                rows = [dict(zip(cols, r)) for r in data_rows]
                            # fallback: try columns + values attributes (numpy/pandas-like)
                            else:
                                cols = list(getattr(content_table, "columns", []))
                                vals = getattr(content_table, "values", None)
                                if vals is not None:
                                    try:
                                        rows_list = vals.tolist()
                                    except Exception:
                                        rows_list = list(vals)
                                    rows = [{cols[i]: r[i] for i in range(len(cols))} for r in rows_list]
                                else:
                                    # last resort: serialize to string
                                    rows = [{"content": str(content_table)}]
                        except Exception as ex:
                            logger.exception("Failed to convert table to records list: %s", ex)
                            raise RuntimeError("Failed to convert table to records list") from ex

                        # attach metadata to each record
                        for r in rows:
                            r.setdefault("reference_name", filename)
                            r.setdefault("reference_size", len(content))
                            r.setdefault("reference_source_url", file_url)

                        result = rows
                    else:
                        content_text = reader.read_text_from_bytes(content, ext=relative_path.split("/")[-1].split(".")[-1])
                        
                        result = [{
                            "name": relative_path.split("/")[-1],
                            "content": content_text,
                            "size": len(content),
                            "url": file_url
                        }]

                    # Save file if path provided
                    if save_path:
                        import os
                        os.makedirs(save_path, exist_ok=True)
                        file_path = os.path.join(save_path, relative_path.split("/")[-1])
                        with open(file_path, "wb") as f:
                            f.write(content)
                        logger.info("File saved to: %s", file_path)

                    return result

                except Exception as ex:
                    logger.error("Failed to download file: %s", ex)
                    raise

            else:
                # Handle list/folder content retrieval
                try:
                    if relative_path.startswith('_api/'):
                        try:
                            # Setup REST call
                            method = kwargs.get("method", "GET").upper()
                            url = f"{self._site_url.rstrip('/')}/{relative_path.lstrip('/')}"
                            headers = {
                                "Authorization": f"Bearer {self._list_token}",
                                "Accept": "application/json;odata=verbose"
                            }
                            params = kwargs.get("params", None)
                            
                            # Execute REST call
                            response_raw = requests.request(method, url, headers=headers, params=params, timeout=30)
                            response_raw.raise_for_status()
                            
                            # Parse JSON response
                            response_json = response_raw.json()
                            
                            # Extract list items from SharePoint REST response
                            if 'd' in response_json and 'results' in response_json['d']:
                                items = response_json['d']['results']
                            elif 'value' in response_json:
                                items = response_json['value']
                            else:
                                items = []
                                
                            if not items:
                                logger.warning("No items found in SharePoint list response")
                                return []
                                
                            # Convert to DataFrame and clean up
                            df = pd.DataFrame(items)
                            
                            # Remove metadata columns (starting with '__')
                            # Remove columns not in sp_list_columns_to_keep                            
                            cols_to_keep = [col for col in df.columns if col in self.config.get("sp_list_columns_to_keep", [])]
                            df = df[cols_to_keep]
                            
                            # Convert DataFrame to list of dictionaries
                            results = df.to_dict('records')
                            
                            # Add metadata to each row
                            for row in results:
                                row['reference_list_name'] = relative_path.split("'")[-2] if "'" in relative_path else relative_path
                                row['reference_site_url'] = self._site_url
                                
                            logger.info(f"Retrieved {len(results)} items from SharePoint list")
                            return results
                            
                        except Exception as ex:
                            logger.error(f"Failed to process SharePoint list data: {str(ex)}")
                            raise
                    else:
                        # Assume it's a folder path
                        folder_url = f"https://graph.microsoft.com/v1.0/sites/{self._site_id}/drives/{self._drive_id}/root:/{relative_path}/children"
                        folder_response = requests.get(folder_url, headers={"Authorization": f"Bearer {self._access_token}"})
                        folder_response.raise_for_status()
                        items = folder_response.json().get('value', [])

                        results = []
                        for item in items:
                            results.append({
                                "name": item["name"],
                                "url": item["webUrl"],
                                "size": item.get("size"),
                                "created": item.get("createdDateTime"),
                                "modified": item.get("lastModifiedDateTime")
                            })
                        return results

                except Exception as ex:
                    logger.error("Failed to fetch SharePoint data: %s", ex)
                    raise

        except Exception as ex:
            logger.exception("SharePointSource.fetch_data failed")
            raise