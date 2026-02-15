from uuid import UUID

from fastapi import HTTPException, status

from app.dependencies.http import CurrentUserDepends
from app.managers import Managers
from app.routers.api.base import Router
from app.schemas.user_forms import (
    UserFormCreateSchema,
    UserFormSchemaWithoutQrcode,
    UserFormSchemaWithQrcode,
    UserFormUpdateSchema,
)


router = Router(
    name="User Forms",
    description="""
API for managing user-created forms.
Each form is associated with a specific user.
""",
)


@router.post(
    "/forms",
    status_code=status.HTTP_201_CREATED,
    response_model=UserFormSchemaWithoutQrcode,
)
async def create_form(
    data: UserFormCreateSchema,
    current_user: CurrentUserDepends,
) -> UserFormSchemaWithoutQrcode:
    """
    Create a new form for the current user.

    ### Input
    - **title** [max 128 chars]
    - **description** [max 256 chars]

    ### Output
    - **created_at**: creation datetime
    - **updated_at**: last update datetime
    - **id**: form UUID
    - **title**: form title
    - **user_id**: the UUID of the user who created the form
    - **description**: form description
    - **is_unable**: whether the form is active or not
    """
    return await Managers.user_forms.create_form(user_id=current_user.id, data=data)


@router.get(
    "/forms",
    status_code=status.HTTP_200_OK,
    response_model=list[UserFormSchemaWithQrcode],
)
async def list_forms(
    current_user: CurrentUserDepends,
) -> list[UserFormSchemaWithQrcode]:
    """
    Retrieve all forms created by the current user.

    ### Input
     - **user_id**: the UUID of the user who created the form

    ### Output
    For each form:
    - **created_at**: creation datetime
    - **updated_at**: last update datetime
    - **id**: form UUID
    - **title**: form title
    - **user_id**: the UUID of the user who created the form
    - **description**: form description
    - **is_unable**: whether the form is active or not
    - **qrcode**: the QRCode of the form
    """
    return await Managers.user_forms.get_list(user_id=current_user.id)


@router.get(
    "/forms/all",
    status_code=status.HTTP_200_OK,
    response_model=list[UserFormSchemaWithQrcode],
)
async def list_all_forms(
    current_user: CurrentUserDepends,
) -> list[UserFormSchemaWithQrcode]:
    """
    Retrieve all forms for user in the system.
    Accessible only by superusers.

    ### Input
    - **form_id** form UUID

    ### Output
    For each form:
    - **created_at**: creation datetime
    - **updated_at**: last update datetime
    - **id**: form UUID
    - **title**: form title
    - **user_id**: the UUID of the user who created the form
    - **description**: form description
    - **is_unable**: whether the form is active or not
    - **qrcode**: the QRCode of the form
    """

    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource",
        )

    return await Managers.user_forms.get_all_forms(user_id=current_user.id)


@router.get(
    "/forms/{form_id}",
    status_code=status.HTTP_200_OK,
    response_model=UserFormSchemaWithoutQrcode,
)
async def get_form(
    form_id: UUID,
    current_user: CurrentUserDepends,
) -> UserFormSchemaWithoutQrcode:
    """
    Retrieve a form by its UUID.

    ### Input
    - **form_id** form UUID

    ### Output
    - **created_at**: creation datetime
    - **updated_at**: last update datetime
    - **id**: form UUID
    - **title**: form title
    - **user_id**: the UUID of the user who created the form
    - **description**: form description
    - **is_unable**: whether the form is active or not
    """
    return await Managers.user_forms.get_form(form_id=form_id, user_id=current_user.id)


@router.patch(
    "/forms/{form_id}",
    status_code=status.HTTP_200_OK,
    response_model=UserFormSchemaWithoutQrcode,
)
async def update_form(
    form_id: UUID,
    data: UserFormUpdateSchema,
    current_user: CurrentUserDepends,
) -> UserFormSchemaWithoutQrcode:
    """
    Partially update a form (HTML page).

    ### Input
    - **form_id** (path): form UUID
    - **title** [max 128 chars]
    - **description** [max 256 chars]

    ### Output
    - **created_at**: creation datetime
    - **updated_at**: last update datetime
    - **id**: form UUID
    - **title**: form title
    - **user_id**: the UUID of the user who created the form
    - **description**: form description
    - **is_unable**: whether the form is active or not
    """
    return await Managers.user_forms.update_form(form_id=form_id, user_id=current_user.id, data=data)


@router.delete(
    "/forms/{form_id}",
    status_code=status.HTTP_200_OK,
    response_model=UserFormSchemaWithoutQrcode,
)
async def delete_form(
    form_id: UUID,
    current_user: CurrentUserDepends,
) -> UserFormSchemaWithoutQrcode:
    """
    Delete a form

    ### Input
    - **form_id** form UUID

    ### Output
    - **created_at**: creation datetime
    - **updated_at**: last update datetime
    - **id**: form UUID
    - **title**: form title
    - **user_id**: the UUID of the user who created the form
    - **description**: form description
    - **is_unable**: whether the form is active or not
    """

    return await Managers.user_forms.delete_form(form_id=form_id, user_id=current_user.id)
