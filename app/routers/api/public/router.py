from uuid import UUID

from fastapi import status
from fastapi.responses import StreamingResponse

from app.managers import Managers
from app.routers.api.base import Router
from app.schemas.user_forms import UserFormSchemaWithoutQrcode
from app.views.public_page import user_forms as views


router = Router(
    name="Public Page",
    description="Public endpoints for viewing forms without authentication.",
)


@router.get(
    "/{form_id}/qrcode",
    status_code=status.HTTP_200_OK,
    response_class=StreamingResponse,
)
async def get_form_qrcode(form_id: UUID):
    """
    Get public PNG QR code for the form.

    ### Input
    - **form_id**: form UUID

    ### Output
    - `200 OK`: image/png
    - `404 Not Found`: if form or QR code not found
    """
    qrcode_bytes = await Managers.user_forms.get_qrcode(form_id=form_id)
    return views.qrcode_response(qrcode_bytes, form_id)


@router.get(
    "/{form_id}",
    status_code=status.HTTP_200_OK,
    response_model=UserFormSchemaWithoutQrcode,
)
async def get_public_form_page(
    form_id: UUID,
):
    """
    Render a public HTML page for a form.

    ### Input
    - **form_id**: form UUID

    ### Output
    - `200 OK`: HTML page with the form data
    - `404 Not Found`: if the form does not exist
    """
    return await Managers.user_forms.get_public_form(form_id=form_id)
