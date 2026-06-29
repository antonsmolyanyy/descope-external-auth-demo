import os

from fastmcp import FastMCP
from fastmcp.server.auth.providers.descope import DescopeProvider


def get_base_url() -> str:
    base_url = os.getenv("BASE_URL")
    if base_url:
        return base_url.rstrip("/")

    vercel_url = os.getenv("VERCEL_URL")
    if vercel_url:
        return f"https://{vercel_url.rstrip('/')}"

    return "http://localhost:8000"


def get_descope_config_url() -> str:
    config_url = os.getenv("DESCOPE_CONFIG_URL")
    if not config_url:
        raise RuntimeError(
            "DESCOPE_CONFIG_URL is required. Set your Descope MCP server "
            "OpenID configuration URL."
        )
    return config_url


auth_provider = DescopeProvider(
    config_url=get_descope_config_url(),
    base_url=get_base_url(),
)
mcp = FastMCP(name="descope-demo", auth=auth_provider)


@mcp.tool
def read_file(path: str) -> str:
    try:
        with open(path, "r") as file:
            return file.read()
    except Exception as e:
        return f"Error reading file: {e}"


@mcp.tool
def write_file(path: str, content: str) -> str:
    try:
        with open(path, "w") as file:
            file.write(content)
        return "File written successfully"
    except Exception as e:
        return f"Error writing file: {e}"


@mcp.tool
def delete_file(path: str) -> str:
    try:
        if os.path.exists(path):
            os.remove(path)
            return "File deleted successfully"
        else:
            return "File does not exist"
    except Exception as e:
        return f"Error deleting file: {e}"


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    mcp.run(transport="http", port=port)
