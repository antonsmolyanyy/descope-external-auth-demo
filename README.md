# Demo External Auth MCP

Descope-protected [FastMCP](https://gofastmcp.com) demo server with file read/write/delete tools. The server is configured for Render deployment with `uv`.

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
uv run python -m py_compile demo_server.py server.py
uv run python -c "from server import app; print(app)"
```
