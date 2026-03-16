from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

try:  # pragma: no cover - exercised when FastAPI is installed
    from fastapi import APIRouter, FastAPI, File, Form, HTTPException, UploadFile
    from fastapi.responses import JSONResponse
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

    class UploadFile:  # pragma: no cover - stub only
        def __init__(self, filename: str = "", content_type: str | None = None, data: bytes = b"") -> None:
            self.filename = filename
            self.content_type = content_type
            self._data = data

        async def read(self) -> bytes:
            return self._data

    class HTTPException(Exception):
        def __init__(self, status_code: int, detail: Any) -> None:
            super().__init__(detail)
            self.status_code = status_code
            self.detail = detail

    class JSONResponse(dict):
        def __init__(self, *, status_code: int, content: Any) -> None:
            super().__init__(content=content, status_code=status_code)

    def File(default: Any = None) -> Any:  # pragma: no cover - stub only
        return default

    def Form(default: Any = None) -> Any:  # pragma: no cover - stub only
        return default
