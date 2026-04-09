# Environment Configuration (`.env`)

This file documents the environment variables used by `test_mcp_server` and provides a safe template with sensitive values redacted.

## Security First

- Never commit real secrets (client IDs, client secrets, tenant IDs, tokens) to Git.
- Keep real values only in your local `.env`.
- Share only masked values like `<your-client-id>` in docs, tickets, or screenshots.

## Safe `.env` Template

Use the following template for onboarding and documentation:

```env
# Generic server identity
MCP_SERVER_NAME=generic-mcp-server

# Logging
LOG_LEVEL=INFO

# MCP runtime
MCP_HOST=0.0.0.0
MCP_PORT=8000
MCP_TRANSPORT=streamable-http
MCP_PATH=/mcp

# Health endpoint runtime
ENABLE_HEALTH_SERVER=true
HEALTH_HOST=0.0.0.0
HEALTH_PORT=8081

# Inbound MCP auth (Entra as external AS)
MCP_AUTH_ENABLED=false
AZURE_TENANT_ID=<your-entra-tenant-id>
AZURE_CLIENT_ID=<your-entra-app-client-id>
MCP_AUTH_REQUIRED_SCOPES=api://<your-client-id>/.default
MCP_AUTH_BASE_URL=https://<your-aca-app-fqdn>.azurecontainerapps.io

# Pega outbound API settings
PEGA_BASE_URL=https://<your-pega-host>
PEGA_APPLICATION_API_BASE=https://<your-pega-host>/prweb/app/<your-app>/api/application/v2
PEGA_OAUTH_TOKEN_URL=https://<your-pega-host>/prweb/PRRestService/oauth2/v1/token
PEGA_CLIENT_ID=<your-pega-client-id>
PEGA_CLIENT_SECRET=<your-pega-client-secret>
PEGA_SCOPE=

# Case create defaults and limits
ALLOWED_CASE_TYPE_ID=<your-case-type-id>
ALLOWED_CREATE_PROCESS_ID=pyStartCase
DEFAULT_ORIGIN_CHANNEL=Mobile
DEFAULT_CREATE_CONTENT_JSON={"Description":"Created by MCP server","Priority":"High","Title":"MCP Product Management Case"}
MAX_CREATE_PAYLOAD_BYTES=25000
CREATE_CALLS_PER_MINUTE_LIMIT=20

# HTTP/timeouts
REQUEST_TIMEOUT_SECONDS=30
TOKEN_REFRESH_SKEW_SECONDS=60
```

## Required vs Optional

- Required for Pega calls:
  - `PEGA_BASE_URL`
  - `PEGA_CLIENT_ID`
  - `PEGA_CLIENT_SECRET`
- Usually required (unless defaults fit your deployment):
  - `PEGA_APPLICATION_API_BASE`
  - `PEGA_OAUTH_TOKEN_URL`
  - `ALLOWED_CASE_TYPE_ID`
- Optional:
  - `PEGA_SCOPE`
  - Inbound auth variables when `MCP_AUTH_ENABLED=false`

## Quick Validation

After updating `.env`, run the server and verify:

1. Token fetch succeeds.
2. `pega_create_case` works.
3. `pega_add_attachment` works.

If one fails, verify URL, client ID/secret, and case type/process IDs first.
