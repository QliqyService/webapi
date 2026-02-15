from fastapi import Request

from app.routers.api.base import Router
from app.schemas.shared import GetHealthcheckResponse


router = Router(
    name="Shared",
    description="Operations on shared endpoints",
)


@router.get("/healthcheck", response_model=GetHealthcheckResponse)
async def healthcheck(request: Request):
    return GetHealthcheckResponse(msg="OK", release=request.app.settings.APP_RELEASE)
