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
        if not query_id:
            raise ValueError("AzureDevOpsSource.fetch_data requires 'query_id' or query argument")

        base = f"https://dev.azure.com/{org}/"
        if project:
            base = f"{base}{project}/"
        # WIQL query by id (returns list of work item refs)
        wiql_url = f"{base}_apis/wit/wiql/{query_id}"
        params = {"api-version": api_version}
        method = self.config.get("method", "GET").upper()
        query_response = requests.request(method, wiql_url, headers=getattr(self, "_headers", {}), params=params)
        query_response.raise_for_status()

        if query_response.status_code != 200:
            raise RuntimeError(f"Error: {query_response.status_code}")

        work_items_refs = query_response.json().get('workItems', []) or []
        if not work_items_refs:
            return []

        # collect ids and fetch details in batch to get all fields for all work item types
        ids = [str(item.get('id')) for item in work_items_refs if item.get('id')]
        if not ids:
            return []

        details_url = f"https://dev.azure.com/{org}/{project}/_apis/wit/workitems"
        # expand=all to include fields, relations, and attachments
        params = {
            "ids": ",".join(ids),
            "api-version": api_version,
            "$expand": "all"
        }
        details_resp = requests.get(details_url, headers=getattr(self, "_headers", {}), params=params)
        details_resp.raise_for_status()
        items = details_resp.json().get("value", [])

        work_item_details: List[Dict[str, Any]] = []
        for item in items:
            item_id = item.get("id")
            fields = item.get("fields", {}) or {}

            # Normalize field keys to safe snake_case-like keys
            norm_fields: Dict[str, Any] = {}
            for k, v in fields.items():
                nk = k.replace(".", "_")
                nk = nk.lower()
                norm_fields[nk] = v

            # Helper to safely extract nested displayName for assigned to
            assigned = norm_fields.get("system_assignedto")
            if isinstance(assigned, dict):
                assigned_to = assigned.get("displayName") or assigned.get("uniqueName") or str(assigned)
            else:
                assigned_to = assigned

            # find a description-like field (some types use different field names)
            desc = ""
            for fk in ["system_description", "microsoft_vsts_createdby", "html_description"]:
                if fk in norm_fields:
                    desc = norm_fields.get(fk) or ""
                    break
            if not desc:
                # fallback: first field key that contains 'description'
                for kf, vf in norm_fields.items():
                    if "description" in kf and vf:
                        desc = vf
                        break

            # clean HTML description to text
            try:
                c_desc = BeautifulSoup(desc or "", "html.parser").get_text()
            except Exception:
                c_desc = desc or ""

            # Build common convenience values (use available fields)
            wi_type = norm_fields.get("system_workitemtype") or norm_fields.get("system_witype") or ""
            title = norm_fields.get("system_title") or ""
            status = norm_fields.get("system_state") or ""
            created = norm_fields.get("system_createddate") or norm_fields.get("system_created") or ""
            changed = norm_fields.get("system_changeddate") or norm_fields.get("system_changed") or ""
            tags = norm_fields.get("system_tags", "")
            project_name = norm_fields.get("custom.projectname") or norm_fields.get("system_teamproject") or ""

            rtype = norm_fields.get("custom.releasetype") or norm_fields.get("custom_releasetype") or ""
            target_date = norm_fields.get("microsoft_vsts_scheduling_targetdate") or norm_fields.get("microsoft.vsts.scheduling.targetdate") or ""

            # Construct a 'full' description string using available pieces
            parts = []
            if wi_type:
                parts.append(f"{wi_type} ID {item_id}")
            else:
                parts.append(f"WorkItem {item_id}")
            if created:
                parts.append(f"was created on {created}")
            if title:
                parts.append(f"and has Title '{title}'")
            if status:
                parts.append(f"is currently in {status} state")
            if assigned_to:
                parts.append(f"is assigned to {assigned_to}")
            if project_name:
                parts.append(f"for Project '{project_name}'")
            if rtype:
                parts.append(f"release type '{rtype}'")
            if target_date:
                parts.append(f"with target date '{target_date}'")
            if tags:
                parts.append(f"Tags: {tags}")
            if c_desc:
                parts.append(f"Description: [{c_desc}]")
            fullfeature = ". ".join(parts)

            # include all normalized fields in the returned object for completeness
            entry = {
                "id": item_id,
                "type": wi_type,
                "title": title,
                "status": status,
                "assigned_to": assigned_to,
                "created": created,
                "changed_date": changed,
                "tags": tags,
                "project": project_name,
                "release_type": rtype,
                "target_date": target_date,
                "description": c_desc,
                "full": fullfeature
            }
            work_item_details.append(entry)

        return work_item_details
