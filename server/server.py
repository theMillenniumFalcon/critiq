"""Compatibility runner for the Critiq FastAPI app.

This file exposes an `app` ASGI object and provides a small
``__main__`` runner so you can start the development server by running
this file directly or by using an ASGI server.

Usage examples:
- Run with uvicorn pointing at the module:
    uvicorn server.server:app --reload

- Run the file directly (calls ``uvicorn.run``):
    python server/server.py

If you run the script from inside the ``server/`` folder, the runner
automatically uses the local module path (``app.main:app``) so the
script works when executed as ``python server.py`` from that
directory.
"""

# Try package-style import first so `uvicorn server.server:app` works
try:
    from server.app.main import app
except Exception:
    # Fallbacks for running the file directly from inside the server/ dir
    try:
        # When running as a script inside server/ (python server.py)
        from app.main import create_app
        app = create_app()
    except Exception:
        # Final fallback: import dynamically via import_module
        from importlib import import_module

        mod = import_module("server.app.main")
        app = getattr(mod, "app", None)
        if app is None:
            create = getattr(mod, "create_app", None)
            if create is None:
                raise RuntimeError("Could not import FastAPI app from server.app.main")
            app = create()


if __name__ == "__main__":
    import os
    import uvicorn

    # If running the script from inside the `server/` directory, use the
    # local module path so imports resolve correctly (this makes
    # `python server.py` inside server/ behave as expected). Otherwise
    # use the package module path which is useful when running from the
    # repository root.
    cwd_basename = os.path.basename(os.path.abspath(os.getcwd()))
    if cwd_basename == "server":
        target = "app.main:app"
    else:
        target = "server.server:app"

    uvicorn.run(target, host="127.0.0.1", port=8000, reload=True)
