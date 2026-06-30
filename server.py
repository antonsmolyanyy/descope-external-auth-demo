from fastapi import FastAPI
from fastapi.responses import JSONResponse

from demo_server import get_base_url, get_mcp


def build_app() -> FastAPI:
    try:
        mcp_app = get_mcp().http_app(stateless_http=True)
    except Exception as exc:
        error_message = str(exc)
        app = FastAPI()

        @app.get("/")
        async def misconfigured_root() -> JSONResponse:
            return JSONResponse(
                {
                    "error": error_message,
                    "required_env": ["DESCOPE_CONFIG_URL", "BASE_URL"],
                },
                status_code=503,
            )

        return app

    app = FastAPI(lifespan=mcp_app.lifespan)

    @app.get("/")
    async def root() -> dict[str, str]:
        base_url = get_base_url()
        return {
            "status": "ok",
            "mcp_endpoint": f"{base_url}/mcp",
            "protected_resource_metadata": f"{base_url}/.well-known/oauth-protected-resource/mcp",
        }

    app.mount("/", mcp_app)
    return app


app = build_app()
