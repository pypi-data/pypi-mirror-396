from typing import Any, Dict, List, Optional
from datasourcelib.datasources.datasource_base import DataSourceBase
from datasourcelib.utils.logger import get_logger
from datasourcelib.utils.validators import require_keys
import base64
import json
from bs4 import BeautifulSoup

logger = get_logger(__name__)

try:
    import requests  # type: ignore
except Exception:
    requests = None  # lazy import handled at runtime

class AzureDevOpsSource(DataSourceBase):
   
    def validate_config(self) -> bool:
        try:
            require_keys(self.config, ["ado_organization", "ado_personal_access_token","ado_project","ado_query_id"])
            return True
        except Exception as ex:
            logger.error("AzureDevOpsSource.validate_config: %s", ex)
            return False

    def connect(self) -> bool:
        if requests is None:
            raise RuntimeError("requests package is required for AzureDevOpsSource")
        # No persistent connection; store auth header
        pat = self.config.get("ado_personal_access_token")
        token = pat
        token_b64 = base64.b64encode(token.encode("utf-8")).decode("utf-8")
        self._headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        self._connected = True
        logger.info("AzureDevOpsSource ready (no persistent connection required)")
        return True

    def disconnect(self) -> None:
        self._headers = {}
        self._connected = False
        logger.info("AzureDevOpsSource cleared")

    def fetch_data(self, query: Optional[str] = None, **kwargs) -> List[Dict[str, Any]]:
        if requests is None:
            raise RuntimeError("requests package is required for AzureDevOpsSource")
        if not getattr(self, "_connected", False):
            self.connect()

        org = self.config.get("ado_organization")
        project = self.config.get("ado_project")
        query_id = self.config.get("ado_query_id")
        api_version = self.config.get("api_version", "7.1")
        #path = self.config.get("query_path", query or "")
        if not query_id:
            raise ValueError("AzureDevOpsSource.fetch_data requires 'query_id' or query argument")

        base = f"https://dev.azure.com/{org}/"
        if project:
            base = f"{base}{project}/"
        url = f"{base}_apis/wit/wiql/{query_id}"
        params = {"api-version": api_version}
        method = self.config.get("method", "GET").upper()
        query_response = requests.request(method, url, headers=getattr(self, "_headers", {}), params=params) #, json=self.config.get("payload")
        query_response.raise_for_status()
        #data = resp.json()
        # Check if the request was successful
        if query_response.status_code == 200:
            work_items = query_response.json()['workItems']
            work_item_details = []

            # Loop through each work item ID to get detailed information
            for item in work_items:
                work_item_id = item['id']
                work_item_url = f'https://dev.azure.com/{org}/{project}/_apis/wit/workitems/{work_item_id}?api-version=7.1'
                work_item_response = requests.get(work_item_url, headers=getattr(self, "_headers", {}))

                if work_item_response.status_code == 200:
                    logger.info(f"Current Item: {work_item_id}")
                    text = work_item_response.json()['fields']['System.Description']
                    c_desc=BeautifulSoup(text, "html.parser").get_text()
                    c_changedate = work_item_response.json()['fields']['System.ChangedDate']
                    c_title = work_item_response.json()['fields']['System.Title'] 
                    c_status = work_item_response.json()['fields']['System.State']
                    c_type = work_item_response.json()['fields']['System.WorkItemType']
                    c_created = work_item_response.json()['fields']['System.CreatedDate']
                    
                    default_value = "-VALUE NOT ASSIGNED-"
                    c_assigned = work_item_response.json()['fields'].get('System.AssignedTo',{}).get('displayName',default_value) 
                    logger.info(c_assigned)
                    c_tags = work_item_response.json()['fields'].get('System.Tags',default_value)
                    c_project = work_item_response.json()['fields'].get('Custom.ProjectName',default_value)
                    c_rtype = work_item_response.json()['fields'].get('Custom.Releasetype',default_value)
                    c_rdate = work_item_response.json()['fields'].get('Microsoft.VSTS.Scheduling.TargetDate',default_value)
                                    
                    #fullfeature = f"{c_type} ID {work_item_id} was created on {c_created} for a {c_rtype} release of Project '{c_project}' with target date '{c_rdate}' and has given Title as '{c_title}'. {c_type} ID {work_item_id} is currently in {c_status} state. {c_type} ID {work_item_id} is assigned to {c_assigned} and last modified on {c_changedate}.Tags Applied to {c_type} ID {work_item_id} are {c_tags}. Full Description of {c_type} ID {work_item_id} is [{c_desc}]."
                    fullfeature = f"{c_type} ID {work_item_id} was created on {c_created}. {c_type} ID {work_item_id}  is a {c_rtype} release of Project '{c_project}'. {c_type} ID {work_item_id} Release has target date '{c_rdate}'.{c_type} ID {work_item_id} has given Title as '{c_title}'. {c_type} ID {work_item_id} is currently in {c_status} state. {c_type} ID {work_item_id} is assigned to {c_assigned}. {c_type} ID {work_item_id} is last modified on {c_changedate}. Tags Applied to {c_type} ID {work_item_id} are {c_tags}. Full Description of {c_type} ID {work_item_id} is [{c_desc}]."
                    # Ensure work_item_details is a list and append a dict for this work item
                    
                    work_item_details.append({
                        "id": work_item_id,
                        "type": c_type,
                        "title": c_title,
                        "status": c_status,
                        "assigned_to": c_assigned,
                        "created": c_created,
                        "changed_date": c_changedate,
                        "tags": c_tags,
                        "release_type": c_rtype,
                        "target_date": c_rdate,
                        "project": c_project,
                        "description": c_desc,
                        "full": fullfeature
                    })
                else:
                    logger.error(f"Error fetching details for work item ID {work_item_id}: {work_item_response.status_code}")
            
            #work_item_desc = []
            #for desc in work_item_details:
            #    work_item_desc.append(desc['fields']['System.Description'])
                
                
            return work_item_details  #[{"response": json.dumps(work_item_details)}]
        else:
            raise RuntimeError(f"Error: {query_response.status_code}")
        # Caller decides how to interpret the payload; default: return raw json in a single-item list
        