from fastmcp import FastMCP
from fastmcp.server.auth.providers.descope import DescopeProvider
import os

# The DescopeProvider automatically discovers Descope endpoints
# and configures JWT token validation
auth_provider = DescopeProvider(
    config_url="https://api.descope.com/v1/apps/agentic/P3EhOa8sStPIjOyCeedrE5SYGxIu//.well-known/openid-configuration",        # Your MCP Server .well-known URL
    base_url="https://5391-50-145-2-114.ngrok-free.app",                  # Your server's public URL
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
    mcp.run(transport="http", port=8000)