from app.routers.api.auth import router as auth_router
from app.routers.api.base import Router
from app.routers.api.comments import router as comments_router
from app.routers.api.shared import router as shared_router
from app.routers.api.user_forms import router as user_forms_router
from app.routers.api.users import router as users_router


__all__ = ["api_router"]

api_router = Router(prefix="/api/v1")

api_router.include_router(shared_router, prefix="/shared")
api_router.include_router(auth_router, prefix="/auth")
api_router.include_router(user_forms_router, prefix="/form")
api_router.include_router(comments_router, prefix="/comments")
api_router.include_router(users_router, prefix="/user")
