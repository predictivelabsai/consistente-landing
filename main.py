"""
Entrypoint. Kept as a thin shim so the existing Docker CMD (`python main.py`)
continues to work without Dockerfile changes. All routing lives in app.py.
"""

from app import app, serve  # noqa: F401

if __name__ == "__main__":
    serve()
