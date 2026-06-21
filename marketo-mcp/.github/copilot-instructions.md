# Copilot Instructions for Marketo MCP

- This project is a Python MCP server built with the MCP Python SDK and `FastMCP`.
- Prefer stdio transport and keep tool implementations thin wrappers over the Marketo REST API.
- Use `httpx` for outbound API calls.
- Keep authentication token handling centralized in `src/marketo_mcp/server.py`.
- The OpenAPI source of truth is the attached Marketo REST specification.
- Follow the MCP documentation and Python SDK patterns from modelcontextprotocol.io when extending tools.
