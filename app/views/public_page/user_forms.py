from uuid import UUID

from fastapi.requests import Request
from starlette.responses import HTMLResponse, StreamingResponse

from app.schemas.user_forms import UserFormSchemaWithQrcode
from app.views.utils import template


def qrcode_response(qrcode: bytes, form_id: UUID) -> StreamingResponse:
    return StreamingResponse(
        iter([qrcode]),
        media_type="image/png",
        headers={
            "Content-Disposition": f'inline; filename="form-{form_id}-qrcode.png"',
        },
    )


def get_public(request: Request, form: UserFormSchemaWithQrcode) -> HTMLResponse:
    return template(
        request,
        "user_forms/get_public.html",
        {"title": "Публичная форма", "form": form},
    )
