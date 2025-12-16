from typing import Any, Dict, List, Optional
from datasourcelib.datasources.datasource_base import DataSourceBase
from datasourcelib.utils.logger import get_logger
from datasourcelib.utils.validators import require_keys
import base64
import json
from bs4 import BeautifulSoup
import regex as re

logger = get_logger(__name__)

try:
    import requests  # type: ignore
except Exception:
    requests = None  # lazy import handled at runtime

class AzureDevOpsSource(DataSourceBase):
   
    def validate_config(self) -> bool:
        try:
            require_keys(self.config, ["ado_organization", "ado_personal_access_token"])
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

    @staticmethod
    def sanitize(s: str) -> str:
        """Keep only A-Z a-z 0-9 underscore/dash/equals in a safe way."""
        # using the `regex` import already present as `re`
        return re.sub(r'[^A-Za-z0-9_\-=]', '', s)

    def disconnect(self) -> None:
        self._headers = {}
        self._connected = False
        logger.info("AzureDevOpsSource cleared")

    def fetch_query_data(self, query: Optional[str] = None, **kwargs) -> List[Dict[str, Any]]:
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

    def fetch_wiki_data(self, wiki_name: Optional[str] = None, max_depth: int = 3, **kwargs) -> List[Dict[str, Any]]:
        """
        Crawl wiki pages in the configured Azure DevOps organization/project and return a list of
        dicts: {"display_name": str, "url": str, "content": str, "wiki": str, "project": str}.
        - wiki_name: optional filter to select a single wiki by name
        - max_depth: how many child levels to traverse (>=1)
        - If ado_project is configured, only fetch wikis from that project.
        - Otherwise, fetch wikis from all projects in the organization.
        """
        if requests is None:
            raise RuntimeError("requests package is required for AzureDevOpsSource")
        if not getattr(self, "_connected", False):
            self.connect()

        org = self.config.get("ado_organization")
        configured_project = self.config.get("ado_project")  # Rename to avoid overwriting in loop
        api_version = self.config.get("api_version", "7.1")
        headers = getattr(self, "_headers", {})

        results: List[Dict[str, Any]] = []
        seen_paths = set()

        # Determine which projects to process
        projects_to_process = []
        if configured_project:
            # Use only the configured project
            projects_to_process = [configured_project]
            logger.info("fetch_wiki_data: Using configured project: %s", configured_project)
        else:
            # Fetch all projects in the organization
            try:
                projects_url = f"https://dev.azure.com/{org}/_apis/projects?api-version={api_version}"
                proj_resp = requests.get(projects_url, headers=headers, timeout=30)
                proj_resp.raise_for_status()
                proj_json = proj_resp.json()
                projects_list = proj_json.get("value", [])
                projects_to_process = [p.get("name") or p.get("id") for p in projects_list if p.get("name") or p.get("id")]
                logger.info("fetch_wiki_data: Found %d projects in organization", len(projects_to_process))
            except Exception as ex:
                logger.exception("Failed to list projects in organization: %s", ex)
                return []

        # Process each project
        for project_name in projects_to_process:
            logger.info("fetch_wiki_data: Processing project: %s", project_name)

            # 1) List wikis in this project
            wikis_url = f"https://dev.azure.com/{org}/{project_name}/_apis/wiki/wikis?api-version={api_version}"
            try:
                resp = requests.get(wikis_url, headers=headers, timeout=30)
                resp.raise_for_status()
                wikis_json = resp.json()
                wikis = wikis_json.get("value", []) if isinstance(wikis_json, dict) else []
            except Exception as ex:
                logger.warning("Failed to list wikis for project %s: %s", project_name, ex)
                continue

            # Filter selected wikis by name if specified
            selected_wikis = []
            for w in wikis:
                name = w.get("name") or w.get("wikiName") or ""
                if wiki_name:
                    if name.lower() == wiki_name.lower():
                        selected_wikis.append(w)
                else:
                    # Include all wikis for this project
                    selected_wikis.append(w)

            if not selected_wikis:
                logger.debug("No wikis found in project %s matching filter (wiki_name=%s)", project_name, wiki_name)
                continue

            # 2) Crawl pages in each wiki
            for wiki in selected_wikis:
                wiki_id = wiki.get("id") or wiki.get("name")
                wiki_display = wiki.get("name") or wiki.get("wikiName") or str(wiki_id)
                logger.info("fetch_wiki_data: Crawling wiki '%s' in project '%s'", wiki_display, project_name)

                # BFS queue of (path, depth). Start at root path "/"
                queue = [("/", 1)]

                while queue:
                    path, depth = queue.pop(0)
                    if depth > max_depth:
                        continue

                    # Pages listing for this path with recursionLevel=1 to get direct children
                    pages_url = (
                        f"https://dev.azure.com/{org}/{project_name}/_apis/wiki/wikis/{wiki_id}/pages"
                        f"?path={path}&recursionLevel=1&api-version={api_version}"
                    )
                    try:
                        p_resp = requests.get(pages_url, headers=headers, timeout=30)
                        p_resp.raise_for_status()
                        p_json = p_resp.json()
                        pages = p_json.get("value") or p_json.get("subPages") or []
                    except Exception as ex:
                        logger.warning("Failed to list pages for wiki %s path %s in project %s: %s", 
                                     wiki_display, path, project_name, ex)
                        pages = []

                    for page in pages:
                        page_path = page.get("path") or "/"
                        # Dedupe by wiki id + project + path
                        key = f"{project_name}:{wiki_id}:{page_path}"
                        if key in seen_paths:
                            continue
                        seen_paths.add(key)

                        # Display name and url
                        display_name = page.get("name") or page.get("pageName") or page_path.strip("/") or "/"
                        url = (
                            page.get("remoteUrl")
                            or page.get("url")
                            or (page.get("_links") or {}).get("web", {}).get("href")
                            or ""
                        )

                        # Fetch page content (includeContent)
                        content_text = ""
                        try:
                            content_url = (
                                f"https://dev.azure.com/{org}/{project_name}/_apis/wiki/wikis/{wiki_id}/pages"
                                f"?path={page_path}&includeContent=true&api-version={api_version}"
                            )
                            c_resp = requests.get(content_url, headers=headers, timeout=30)
                            c_resp.raise_for_status()
                            c_json = c_resp.json()

                            # Page content may be in several places depending on API version
                            if isinstance(c_json, dict):
                                # If API returns page object
                                content_text = (
                                    c_json.get("content")
                                    or (c_json.get("value", [{}])[0].get("content", "") if c_json.get("value") else "")
                                    or c_json.get("text", "")
                                )
                            else:
                                # Fallback to raw bytes
                                content_text = c_resp.content.decode("utf-8", errors="ignore")
                        except Exception as fetch_ex:
                            logger.debug("Failed to fetch content for page %s: %s", display_name, fetch_ex)
                            # Best-effort fallback: try to GET the web url (may return HTML)
                            if url:
                                try:
                                    w_resp = requests.get(url, headers=headers, timeout=30)
                                    w_resp.raise_for_status()
                                    content_text = w_resp.content.decode("utf-8", errors="ignore")
                                except Exception:
                                    content_text = ""
                         # Construct a 'full' description string using available pieces
                        content_text = BeautifulSoup(content_text or "", "html.parser").get_text(),
                        parts = []
                        if display_name:
                            parts.append(f"Wiki Page Name is {display_name}. Page has information  about {display_name}")
                        if project_name:
                            parts.append(f"This page is documented by for Project '{project_name}' and by the team '{project_name}'")
                        if url:
                            parts.append(f"The devops wiki page (url) link to access this page is {url}")
                        if project_name:
                            parts.append(f"These wiki page content refers sharepoint site links and other documents from sharepoint. So to get full detailed steps or contents you need to refer those links with appropriate permissions. This page contents are available on wiki are [{content_text}].")

                        index_content = ". ".join(parts)
                        results.append({
                            "display_name": self.sanitize(display_name.replace(" ", "_").strip()),
                            "page_name": display_name,
                            "url": url,
                            "content": index_content,
                            "project": project_name
                        })

                        # Enqueue child pages
                        if depth < max_depth:
                            # If page has children field, use it
                            children = page.get("children") or []
                            if children:
                                for ch in children:
                                    ch_path = ch.get("path") or ch
                                    queue.append((ch_path, depth + 1))
                            else:
                                # Fallback: attempt to list sub-path under current page path
                                sub_path = page_path.rstrip("/") + "/"
                                queue.append((sub_path, depth + 1))

        logger.info("fetch_wiki_data completed: Retrieved %d wiki pages", len(results))
        return results

    def fetch_data(self, query: Optional[str] = None, **kwargs) -> List[Dict[str, Any]]:
        """
        Dispatch fetch call to either wiki downloader or WIQL/query fetcher.

        Priority:
        1. kwargs['ado_download_wiki'] if provided
        2. self.config['ado_download_wiki'] otherwise

        Accepts same params as fetch_query_data / fetch_wiki_data and returns their output.
        """
        # Determine flag from kwargs first, then config
        download_flag = kwargs.pop("ado_download_wiki", None)
        if download_flag is None:
            download_flag = self.config.get("ado_download_wiki", False)

        # normalize boolean-like strings
        if isinstance(download_flag, str):
            download_flag = download_flag.strip().lower() in ("1", "true", "yes", "y", "on")

        if download_flag:
            # pass query as wiki_name if caller intended, otherwise kwargs forwarded
            return self.fetch_wiki_data(wiki_name=query, **kwargs)
        else:
            return self.fetch_query_data(query=query, **kwargs)
