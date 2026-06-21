from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, Optional

import httpx
from mcp.server.fastmcp import FastMCP


def _clean_params(values: Dict[str, Any]) -> Dict[str, Any]:
    return {key: value for key, value in values.items() if value is not None and value != ""}


@dataclass
class MarketoConfig:
    base_url: str
    client_id: Optional[str]
    client_secret: Optional[str]
    access_token: Optional[str]
    timeout: float = 30.0

    @classmethod
    def from_env(cls) -> "MarketoConfig":
        base_url = os.environ.get("MARKETO_BASE_URL")
        return cls(
            base_url=base_url.rstrip("/"),
            client_id=os.environ.get("MARKETO_CLIENT_ID"),
            client_secret=os.environ.get("MARKETO_CLIENT_SECRET"),
            access_token=os.environ.get("MARKETO_ACCESS_TOKEN"),
            timeout=float(os.environ.get("MARKETO_TIMEOUT", "30")),
        )


class MarketoClient:
    def __init__(self, config: MarketoConfig) -> None:
        self.config = config
        self._client = httpx.Client(timeout=config.timeout)

    def close(self) -> None:
        self._client.close()

    def _token(self) -> str:
        if self.config.access_token:
            return self.config.access_token
        if not self.config.client_id or not self.config.client_secret:
            raise ValueError("Set MARKETO_ACCESS_TOKEN or MARKETO_CLIENT_ID and MARKETO_CLIENT_SECRET")
        response = self._client.get(
            f"{self.config.base_url}/identity/oauth/token",
            params={
                "grant_type": "client_credentials",
                "client_id": self.config.client_id,
                "client_secret": self.config.client_secret,
            },
        )
        response.raise_for_status()
        payload = response.json()
        return payload["access_token"]

    def request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json: Any = None,
        auth: bool = True,
    ) -> Any:
        headers: Dict[str, str] = {}
        if auth:
            headers["Authorization"] = f"Bearer {self._token()}"
        response = self._client.request(
            method,
            f"{self.config.base_url}{path}",
            params=_clean_params(params or {}),
            json=json,
            headers=headers,
        )
        response.raise_for_status()
        if response.headers.get("content-type", "").startswith("application/json"):
            return response.json()
        return {"text": response.text}


config = MarketoConfig.from_env()
client = MarketoClient(config)
mcp = FastMCP("Marketo REST API")


@mcp.tool()
def get_access_token(client_id: str, client_secret: str) -> Dict[str, Any]:
    """Get an OAuth access token using client credentials."""
    return client.request(
        "GET",
        "/identity/oauth/token",
        params={
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
        },
        auth=False,
    )


@mcp.tool()
def search_leads(filter_type: str, filter_values: str, fields: Optional[str] = None, batch_size: Optional[int] = None, next_page_token: Optional[str] = None) -> Dict[str, Any]:
    return client.request(
        "GET",
        "/rest/v1/leads.json",
        params={
            "filterType": filter_type,
            "filterValues": filter_values,
            "fields": fields,
            "batchSize": batch_size,
            "nextPageToken": next_page_token,
        },
    )


@mcp.tool()
def create_update_leads(input: list[dict[str, Any]], action: str = "createOrUpdate", lookup_field: str = "email") -> Dict[str, Any]:
    return client.request("POST", "/rest/v1/leads.json", json={"action": action, "lookupField": lookup_field, "input": input})


@mcp.tool()
def delete_leads(input: list[dict[str, Any]]) -> Dict[str, Any]:
    return client.request("POST", "/rest/v1/leads/delete.json", json={"input": input})


@mcp.tool()
def get_lead_by_id(lead_id: int, fields: Optional[str] = None) -> Dict[str, Any]:
    return client.request("GET", f"/rest/v1/lead/{lead_id}.json", params={"fields": fields})


@mcp.tool()
def describe_leads() -> Dict[str, Any]:
    return client.request("GET", "/rest/v1/leads/describe.json")


@mcp.tool()
def get_lists(id: Optional[int] = None, name: Optional[str] = None, batch_size: Optional[int] = None) -> Dict[str, Any]:
    return client.request("GET", "/rest/v1/lists.json", params={"id": id, "name": name, "batchSize": batch_size})


@mcp.tool()
def get_leads_by_list(list_id: int, fields: Optional[str] = None, batch_size: Optional[int] = None) -> Dict[str, Any]:
    return client.request("GET", f"/rest/v1/list/{list_id}/leads.json", params={"fields": fields, "batchSize": batch_size})


@mcp.tool()
def add_leads_to_list(list_id: int, input: list[dict[str, Any]]) -> Dict[str, Any]:
    return client.request("POST", f"/rest/v1/lists/{list_id}/leads.json", json={"input": input})


@mcp.tool()
def remove_leads_from_list(list_id: int, input: list[dict[str, Any]]) -> Dict[str, Any]:
    return client.request("DELETE", f"/rest/v1/lists/{list_id}/leads.json", json={"input": input})


@mcp.tool()
def get_campaigns(id: Optional[int] = None, name: Optional[str] = None, program_name: Optional[str] = None, batch_size: Optional[int] = None) -> Dict[str, Any]:
    return client.request("GET", "/rest/v1/campaigns.json", params={"id": id, "name": name, "programName": program_name, "batchSize": batch_size})


@mcp.tool()
def trigger_campaign(campaign_id: int, input: Dict[str, Any]) -> Dict[str, Any]:
    return client.request("POST", f"/rest/v1/campaigns/{campaign_id}/trigger.json", json={"input": input})


@mcp.tool()
def schedule_campaign(campaign_id: int, input: Dict[str, Any]) -> Dict[str, Any]:
    return client.request("POST", f"/rest/v1/campaigns/{campaign_id}/schedule.json", json={"input": input})


@mcp.tool()
def get_activity_types() -> Dict[str, Any]:
    return client.request("GET", "/rest/v1/activities/types.json")


@mcp.tool()
def get_paging_token(since_datetime: str) -> Dict[str, Any]:
    return client.request("GET", "/rest/v1/activities/pagingtoken.json", params={"sinceDatetime": since_datetime})


@mcp.tool()
def get_activities(activity_type_ids: str, next_page_token: str, lead_ids: Optional[str] = None, batch_size: Optional[int] = None) -> Dict[str, Any]:
    return client.request("GET", "/rest/v1/activities.json", params={"activityTypeIds": activity_type_ids, "nextPageToken": next_page_token, "leadIds": lead_ids, "batchSize": batch_size})


@mcp.tool()
def get_lead_changes(fields: str, next_page_token: str, batch_size: Optional[int] = None) -> Dict[str, Any]:
    return client.request("GET", "/rest/v1/activities/leadchanges.json", params={"fields": fields, "nextPageToken": next_page_token, "batchSize": batch_size})


@mcp.tool()
def search_companies(filter_type: str, filter_values: str, fields: Optional[str] = None) -> Dict[str, Any]:
    return client.request("GET", "/rest/v1/companies.json", params={"filterType": filter_type, "filterValues": filter_values, "fields": fields})


@mcp.tool()
def create_update_companies(input: list[dict[str, Any]], action: str = "createOrUpdate", dedupe_by: Optional[str] = None) -> Dict[str, Any]:
    return client.request("POST", "/rest/v1/companies.json", json={"action": action, "dedupeBy": dedupe_by, "input": input})


@mcp.tool()
def describe_companies() -> Dict[str, Any]:
    return client.request("GET", "/rest/v1/companies/describe.json")


@mcp.tool()
def search_opportunities(filter_type: str, filter_values: str, fields: Optional[str] = None) -> Dict[str, Any]:
    return client.request("GET", "/rest/v1/opportunities.json", params={"filterType": filter_type, "filterValues": filter_values, "fields": fields})


@mcp.tool()
def create_update_opportunities(input: list[dict[str, Any]], action: str = "createOrUpdate", dedupe_by: Optional[str] = None) -> Dict[str, Any]:
    return client.request("POST", "/rest/v1/opportunities.json", json={"action": action, "dedupeBy": dedupe_by, "input": input})


@mcp.tool()
def describe_opportunities() -> Dict[str, Any]:
    return client.request("GET", "/rest/v1/opportunities/describe.json")


@mcp.tool()
def get_programs(max_return: Optional[int] = None, offset: Optional[int] = None, filter_type: Optional[str] = None, filter_values: Optional[str] = None) -> Dict[str, Any]:
    return client.request("GET", "/asset/v1/programs.json", params={"maxReturn": max_return, "offset": offset, "filterType": filter_type, "filterValues": filter_values})


@mcp.tool()
def get_program_by_id(program_id: int) -> Dict[str, Any]:
    return client.request("GET", f"/asset/v1/program/{program_id}.json")


@mcp.tool()
def get_emails(max_return: Optional[int] = None, offset: Optional[int] = None, status: Optional[str] = None, folder: Optional[str] = None) -> Dict[str, Any]:
    return client.request("GET", "/asset/v1/emails.json", params={"maxReturn": max_return, "offset": offset, "status": status, "folder": folder})


@mcp.tool()
def get_email_by_id(email_id: int) -> Dict[str, Any]:
    return client.request("GET", f"/asset/v1/email/{email_id}.json")


@mcp.tool()
def get_email_content(email_id: int) -> Dict[str, Any]:
    return client.request("GET", f"/asset/v1/email/{email_id}/content.json")


@mcp.tool()
def get_landing_pages(max_return: Optional[int] = None, offset: Optional[int] = None, status: Optional[str] = None) -> Dict[str, Any]:
    return client.request("GET", "/asset/v1/landingPages.json", params={"maxReturn": max_return, "offset": offset, "status": status})


@mcp.tool()
def get_forms(max_return: Optional[int] = None, offset: Optional[int] = None, status: Optional[str] = None) -> Dict[str, Any]:
    return client.request("GET", "/asset/v1/forms.json", params={"maxReturn": max_return, "offset": offset, "status": status})


@mcp.tool()
def get_folders(root: Optional[str] = None, max_depth: Optional[int] = None, max_return: Optional[int] = None, offset: Optional[int] = None) -> Dict[str, Any]:
    return client.request("GET", "/asset/v1/folders.json", params={"root": root, "maxDepth": max_depth, "maxReturn": max_return, "offset": offset})


@mcp.tool()
def get_program_tokens(folder_id: int, folder_type: str) -> Dict[str, Any]:
    return client.request("GET", f"/asset/v1/folder/{folder_id}/tokens.json", params={"folderType": folder_type})


@mcp.tool()
def get_daily_usage() -> Dict[str, Any]:
    return client.request("GET", "/rest/v1/stats/usage.json")


@mcp.tool()
def get_daily_errors() -> Dict[str, Any]:
    return client.request("GET", "/rest/v1/stats/errors.json")


def main() -> None:
    try:
        mcp.run()
    finally:
        client.close()


if __name__ == "__main__":
    main()
