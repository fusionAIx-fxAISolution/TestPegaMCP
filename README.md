# Generic MCP Scaffold

This repository now contains a reusable MCP server scaffold in `mcp_server/`.

The scaffold keeps:

- core `FastMCP` startup and transport wiring
- optional `/healthz` support for probes
- optional inbound Microsoft Entra bearer-token validation
- one minimal `server_health` MCP tool for smoke testing

It intentionally does not include business logic or outbound API clients. See `mcp_server/README.md` for setup and extension details.
