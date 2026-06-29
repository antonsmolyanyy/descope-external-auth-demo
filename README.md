# Demo External Auth MCP

Descope-protected [FastMCP](https://gofastmcp.com) demo server with file read/write/delete tools.

## Environment variables

Copy `.env.example` to `.env` and fill in the values:

| Variable | Required | Description |
| --- | --- | --- |
| `DESCOPE_CONFIG_URL` | Yes | Descope MCP server OpenID configuration URL from the Descope console |
| `BASE_URL` | No | Public URL of this server. Defaults to `http://localhost:8000` locally, or `https://$VERCEL_URL` on Vercel |
| `PORT` | No | Local dev port for `python demo_server.py` (default: `8000`) |
| `FASTMCP_STATELESS_HTTP` | No | Set to `true` on serverless platforms such as Vercel |

## Local development

```bash
uv sync --frozen
cp .env.example .env
# edit .env

uv run python demo_server.py
```

The MCP endpoint is available at `http://localhost:8000/mcp`.

## Deploy to Vercel

Use these project settings:

```text
Root Directory: ./
Build Command: leave empty / None
Output Directory: leave empty / N/A
Install Command: uv sync --frozen
```

Set these environment variables in the Vercel project:

- `DESCOPE_CONFIG_URL`
- `BASE_URL` (recommended: your production URL, e.g. `https://your-app.vercel.app`)
- `FASTMCP_STATELESS_HTTP=true`

Vercel loads the ASGI app from `server.py` as `app`. The MCP endpoint is served at `/mcp`.

After deployment, configure your Descope MCP server and MCP clients to use:

```text
https://your-app.vercel.app/mcp
```

## Sanity checks

```bash
uv sync --frozen
uv run python -m compileall .
uv run python -c "from server import app; print(app)"
```
