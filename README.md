# Demo External Auth MCP

Descope-protected [FastMCP](https://gofastmcp.com) demo server for a fake **NimbusDesk** support workspace. The server is configured for Render deployment with `uv`.

## Support Agent Demo Tools

This MCP server exposes a fake support workspace backed by local JSON files in `data/`. Seed data is created automatically on startup if the files are missing.

### Scopes

Define these scopes on your Descope MCP server so clients can request them during OAuth:

- `kb:read` — search knowledge base articles
- `customers:read` — view customer profiles
- `tickets:read` — view support tickets
- `tickets:write` — create, update, escalate, and close tickets
- `replies:draft` — draft support replies
- `refunds:write` — issue fake refunds
- `audit:read` — view audit logs

Tools without the required scope are hidden from `tools/list`, and direct calls return not-found.

### Tools

| Tool | Scope | Description |
| --- | --- | --- |
| `search_knowledge_base` | `kb:read` | Search KB articles by title, category, body, and keywords |
| `get_customer_profile` | `customers:read` | Look up a customer by ID or email |
| `list_customer_tickets` | `tickets:read` | List tickets for a customer, optionally filtered by status |
| `get_ticket` | `tickets:read` | Get full ticket details with customer summary |
| `draft_support_reply` | `replies:draft` | Generate a deterministic reply draft without modifying the ticket |
| `create_ticket` | `tickets:write` | Create a new support ticket |
| `add_internal_note` | `tickets:write` | Add an internal note to a ticket |
| `escalate_ticket` | `tickets:write` | Escalate a ticket to another team |
| `close_ticket` | `tickets:write` | Close a ticket with a resolution note |
| `issue_refund` | `refunds:write` | Issue a fake refund (blocked above $100) |
| `view_audit_logs` | `audit:read` | View recent audit log entries |

### Example tool-call scenarios

1. Search KB for SAML certificate rotation: `search_knowledge_base("SAML certificate")`
2. Get customer profile: `get_customer_profile("maya.chen@example.com")`
3. List Maya's tickets: `list_customer_tickets("cus_001")`
4. Draft a reply: `draft_support_reply("tic_1001", tone="professional")`
5. Add an internal note: `add_internal_note("tic_1001", "Checked IdP metadata")`
6. Escalate the ticket: `escalate_ticket("tic_1001", "SSO outage", "support-tier-2")`
7. Try a blocked refund: `issue_refund("cus_002", 250.0, "Goodwill credit")` — returns manager approval error
8. Issue a small refund: `issue_refund("cus_002", 50.0, "Seat overage correction", ticket_id="tic_1002")`
9. View audit logs: `view_audit_logs(limit=10)`

## Environment variables

Copy `.env.example` to `.env` and fill in the values:

| Variable | Required | Description |
| --- | --- | --- |
| `DESCOPE_CONFIG_URL` | Yes | Descope MCP server OpenID configuration URL from the Descope console |
| `BASE_URL` | No | Public URL of this server. Defaults to `http://localhost:8000` locally, `$RENDER_EXTERNAL_URL` on Render, or `https://$VERCEL_URL` on Vercel |
| `PORT` | No | Local dev port for `python demo_server.py` (default: `8000`) |

## Local development

```bash
uv sync --frozen
cp .env.example .env
# edit .env

uv run python demo_server.py
```

The MCP endpoint is available at `http://localhost:8000/mcp`.

## Deploy to Render

This directory includes `render.yaml` for Render Blueprint deploys. Use the `mcp-server` directory as the Render service root so `pyproject.toml` and `uv.lock` are in the root of the service.

```text
Runtime: Python
Build Command: uv sync --frozen
Start Command: uv run uvicorn server:app --host 0.0.0.0 --port $PORT
```

Set these environment variables in the Render service:

- `DESCOPE_CONFIG_URL`
- `BASE_URL` (optional if `RENDER_EXTERNAL_URL` is present; recommended for custom domains)

Render starts the ASGI app from `server.py` as `app`. The MCP endpoint is served at `/mcp`.

After deployment, configure your Descope MCP server and MCP clients to use:

```text
https://your-app.onrender.com/mcp
```

## Deploy to Vercel

The legacy Vercel config is still present in `vercel.json`. Use these project settings:

```text
Root Directory: ./
Build Command: leave empty / None
Output Directory: leave empty / N/A
Install Command: uv sync --frozen
```

## Sanity checks

```bash
uv sync --frozen
uv run python -m py_compile demo_server.py server.py data_store.py seed_data.py tools.py
uv run python -c "from server import app; print(app)"
```
