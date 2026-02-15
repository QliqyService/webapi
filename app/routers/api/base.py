from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel


__all__ = ["Router", "RouterMetadata"]


class RouterMetadata(BaseModel):
    """Router metadata"""

    name: str | None = ""
    description: str | None = ""


class Router(APIRouter):
    """API router with metadata"""

    name: str | None
    description: str | None
    tags_metadata: list[dict[str, str]] = []

    def __init__(self, *args: Any, name: str | None = None, description: str | None = None, **kwargs: Any) -> None:
        """Initialize API router with metadata.

        Args:
            name (str | None): name of API router
            description (str | None): description of API router
            *args (Any): positional arguments
            **kwargs (Any): keyword arguments
        """
        self.name = name
        self.description = description
        self.tags_metadata = []
        super().__init__(*args, **kwargs)

    def include_router(self, router: APIRouter, *args: Any, **kwargs: Any) -> None:
        """Include API router with metadata.

        Args:
            router (Router): API router
            *args (Any): positional arguments
            **kwargs (Any): keyword arguments
        """
        if isinstance(router, Router):
            kwargs["tags"] = [router.name] if router.name else []
        super().include_router(*args, router=router, **kwargs)
        self._include_metadata(router)

    def _include_metadata(self, router: APIRouter):
        if isinstance(router, Router):
            self.tags_metadata.append(RouterMetadata(name=router.name, description=router.description).model_dump())
