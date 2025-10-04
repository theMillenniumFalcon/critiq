from fastapi import FastAPI


def create_app() -> FastAPI:
    """Create and configure the FastAPI app instance.

    This minimal factory sets up an in-memory task store at app.state.tasks
    and includes the API v1 routers (analyze + admin).
    """
    app = FastAPI(title="critiq - dev")

    # simple in-memory store for demo/dev purposes
    app.state.tasks = {}

    # import and include routers (local imports to avoid startup-time side-effects)
    from .api.v1 import analyze  # noqa: E402
    from .api.v1 import admin  # noqa: E402

    app.include_router(analyze.router)
    app.include_router(admin.router)

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    return app


app = create_app()


if __name__ == "__main__":
    # simple runner for local development
    import uvicorn

    uvicorn.run("server.app.main:app", host="127.0.0.1", port=8000, reload=True)
