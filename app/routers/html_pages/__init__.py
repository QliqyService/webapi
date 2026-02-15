from app.routers.api import Router
from app.routers.html_pages.auth import router as auth_pages_router
from app.routers.html_pages.comments import router as comments_pages_router
from app.routers.html_pages.forms import router as forms_pages_router


__all__ = ["pages_router"]

pages_router = Router(prefix="/qliqy")
pages_router.include_router(auth_pages_router)
pages_router.include_router(forms_pages_router)
pages_router.include_router(comments_pages_router)
