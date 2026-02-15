from typing import Any, Mapping

from fastapi import Request
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates


templates = Jinja2Templates(directory="app/templates")


def get_api_root(request: Request) -> str:
    return request.scope.get("api_root_path", "") or ""


def template(request: Request, name: str, context: Mapping[str, Any]) -> HTMLResponse:
    """Отрендерить HTML-шаблон, добавив root и api_root в контекст."""
    return templates.TemplateResponse(
        name,
        {
            "request": request,
            "root": get_root(request),
            "api_root": get_api_root(request),
            **context,
        },
    )


def get_root(request: Request) -> str:
    """Вернуть root_path приложения (пустая строка, если не задан)."""
    return request.scope.get("root_path", "") or ""
