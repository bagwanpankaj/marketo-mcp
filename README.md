# Marketo MCP Server

Python MCP server for the Marketo REST API described in as per [Marketo API Documentation](https://experienceleague.adobe.com/en/docs/marketo-developer/marketo/rest/rest-api)

## Environment

Set these environment variables before running:

- `MARKETO_BASE_URL` - Marketo instance URL, for example `https://<munchkin-id>.mktorest.com`
- `MARKETO_CLIENT_ID` - OAuth client id
- `MARKETO_CLIENT_SECRET` - OAuth client secret

Optional:

- `MARKETO_TIMEOUT` - Request timeout in seconds, default `30`
- `MARKETO_ACCESS_TOKEN` - Pre-fetched bearer token to skip OAuth token retrieval

## Run

```bash
cd marketo-mcp
python -m venv .venv
source .venv/bin/activate
pip install -e .
marketo-mcp
```

## Tools

The server exposes tools for the Marketo operations in the OpenAPI spec, including:

- authentication token retrieval
- leads search, create/update, delete, and describe
- list membership operations
- campaign listing, triggering, and scheduling
- activity queries
- company and opportunity operations
- asset listing and retrieval
- usage and error stats
