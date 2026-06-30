import os

from fastmcp import FastMCP
from fastmcp.server.auth.providers.descope import DescopeProvider

from data_store import ensure_data_files
from tools import register_support_tools

_mcp: FastMCP | None = None


def get_base_url() -> str:
    base_url = os.getenv("BASE_URL")
    if base_url:
        return base_url.rstrip("/")

    vercel_url = os.getenv("VERCEL_URL")
    if vercel_url:
        return f"https://{vercel_url.rstrip('/')}"

    render_external_url = os.getenv("RENDER_EXTERNAL_URL")
    if render_external_url:
        return render_external_url.rstrip("/")

    return "http://localhost:8000"


def get_descope_config_url() -> str:
    config_url = os.getenv("DESCOPE_CONFIG_URL")
    if not config_url:
        raise RuntimeError(
            "DESCOPE_CONFIG_URL is required. Set your Descope MCP server "
            "OpenID configuration URL."
        )
    return config_url


def create_mcp() -> FastMCP:
    ensure_data_files()

    auth_provider = DescopeProvider(
        config_url=get_descope_config_url(),
        base_url=get_base_url(),
    )
    mcp = FastMCP(name="Support Agent MCP", auth=auth_provider)
    register_support_tools(mcp)
    return mcp


def get_mcp() -> FastMCP:
    global _mcp
    if _mcp is None:
        _mcp = create_mcp()
    return _mcp


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    get_mcp().run(transport="http", port=port)
