from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

try:  # pragma: no cover - exercised when FastAPI is installed
    from fastapi import APIRouter, FastAPI
except ImportError:  # pragma: no cover - default in scaffold validation
    @dataclass(frozen=True, slots=True)
    class RouteDef:
        method: str
        path: str
        endpoint: str

    class APIRouter:
        def __init__(self, *, prefix: str = "", tags: list[str] | None = None) -> None:
            self.prefix = prefix.rstrip("/")
            self.tags = tags or []
            self.routes: list[RouteDef] = []

        def get(self, path: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
            return self._register("GET", path)

        def post(self, path: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
            return self._register("POST", path)

        def include_router(self, router: "APIRouter") -> None:
            self.routes.extend(router.routes)

        def _register(self, method: str, path: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
            full_path = f"{self.prefix}{path}" if self.prefix else path

            def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
                self.routes.append(RouteDef(method=method, path=full_path, endpoint=func.__name__))
                return func

            return decorator

    class FastAPI(APIRouter):
        def __init__(self, *, title: str) -> None:
            super().__init__(prefix="")
            self.title = title
            self.state = type("State", (), {})()
