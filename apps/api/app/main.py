from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from main import app as runtime_app
from main import build_app_metadata as runtime_build_app_metadata


def build_app_metadata() -> dict[str, Any]:
    return runtime_build_app_metadata()


app = runtime_app
