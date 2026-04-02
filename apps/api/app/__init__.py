"""Versefina API package."""

from __future__ import annotations

import importlib.util
from pathlib import Path


def create_app():
    src_app = Path(__file__).resolve().parents[1] / "src" / "app.py"
    spec = importlib.util.spec_from_file_location("versefina_src_app_for_tests", src_app)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to resolve apps/api/src/app.py.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.create_app()
