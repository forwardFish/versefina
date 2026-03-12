from __future__ import annotations

import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

try:
    from app import create_app
except ImportError:  # pragma: no cover - supports python -m apps.api.src.main
    from .app import create_app

app = create_app()


def build_app_metadata() -> dict[str, object]:
    return {
        "service": "versefina-api",
        "status": "ok",
        "routes": len(getattr(app, "routes", [])),
    }


if __name__ == "__main__":  # pragma: no cover - manual startup path
    try:
        import uvicorn
    except ImportError as exc:  # pragma: no cover
        raise SystemExit("uvicorn is required to run the API locally") from exc

    uvicorn.run("apps.api.src.main:app", host="0.0.0.0", port=8000, reload=False)
