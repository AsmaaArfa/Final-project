"""FastAPI application entrypoint.

This module exposes a top-level `app` object (imported from `api.py`) so
uvicorn can run the application with `python -m uvicorn code.main:app --reload`.
If executed directly, it will start a uvicorn server.
"""

from api import app  # the FastAPI app is defined in api.py

if __name__ == '__main__':
    import uvicorn

    # Run the FastAPI app with reload in development
    uvicorn.run(app, host='0.0.0.0', port=8002, reload=True)
