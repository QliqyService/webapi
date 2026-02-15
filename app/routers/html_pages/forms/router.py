from uuid import UUID

from fastapi import Form, Request, status
from fastapi.responses import HTMLResponse
from starlette.responses import RedirectResponse

from app.dependencies.http import CurrentUserDepends
from app.managers import Managers
from app.routers.api.base import Router
from app.schemas.user_forms import UserFormCreateSchema, UserFormUpdateSchema
from app.views.private_page import user_forms as views
from app.views.public_page import user_forms as public_views


router = Router(name="User Forms (HTML)", description="HTMLResponse user_forms")


@router.get("/forms", response_class=HTMLResponse, status_code=status.HTTP_200_OK, include_in_schema=False)
async def get_list(request: Request, user: CurrentUserDepends):
    """
    Render HTML form get_list page.
    """
    forms = await Managers.user_forms.get_list(user_id=user.id)
    if not forms:
        return RedirectResponse(
            url="/qliqy/create",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    return views.get_list(request=request, forms=forms)


@router.get(
    "/forms/{form_id}",
    response_class=HTMLResponse,
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
async def get_one(
    request: Request,
    form_id: UUID,
    user: CurrentUserDepends,
):
    """
    Render HTML form get page.
    """
    form = await Managers.user_forms.get_form(form_id=form_id, user_id=user.id)
    comments = await Managers.comments.get_list(user_form_id=form_id)
    return views.get_one(request=request, form=form, comments=comments)


@router.get(
    "/create",
    response_class=HTMLResponse,
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
async def get_create(request: Request):
    """
    Render HTML form create page.
    """
    return views.create(request=request)


@router.post(
    "/create",
    response_class=RedirectResponse,
    status_code=status.HTTP_303_SEE_OTHER,
    include_in_schema=False,
)
async def create(
    user: CurrentUserDepends,
    title: str = Form(..., max_length=128),
    description: str = Form(..., max_length=256),
):
    """
    Create form and redirect to form page.
    """
    form = await Managers.user_forms.create_form(
        user_id=user.id,
        data=UserFormCreateSchema(title=title, description=description),
    )
    return RedirectResponse(url=f"/qliqy/forms/{form.id}", status_code=303)


@router.get(
    "/{form_id}/edit",
    response_class=HTMLResponse,
    include_in_schema=False,
)
async def get_update(
    request: Request,
    form_id: UUID,
    user: CurrentUserDepends,
):
    """
    Render HTML form edit page.
    """
    form = await Managers.user_forms.get_form(
        form_id=form_id,
        user_id=user.id,
    )
    return views.update(request=request, form=form)


@router.post(
    "/{form_id}/edit",
    response_class=RedirectResponse,
    status_code=status.HTTP_303_SEE_OTHER,
    include_in_schema=False,
)
async def update(
    form_id: UUID,
    title: str = Form(...),
    description: str = Form(...),
    user: CurrentUserDepends = None,
):
    """
    Update form and redirect to form page.
    """
    data = UserFormUpdateSchema(title=title, description=description)
    await Managers.user_forms.update_form(
        form_id=form_id,
        user_id=user.id,
        data=data,
    )

    return RedirectResponse(url=f"/qliqy/forms/{form_id}", status_code=303)


@router.post(
    "/forms/{form_id}/delete",
    response_class=RedirectResponse,
    status_code=status.HTTP_303_SEE_OTHER,
    include_in_schema=False,
)
async def delete(form_id: UUID, user: CurrentUserDepends):
    """
    Delete form.
    """
    await Managers.user_forms.delete_form(form_id=form_id, user_id=user.id)
    return RedirectResponse(url="/qliqy/forms", status_code=303)


@router.get(
    "/public/forms/{form_id}",
    response_class=HTMLResponse,
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
async def get_public(request: Request, form_id: UUID):
    form = await Managers.user_forms.get_public_form(form_id=form_id)
    return public_views.get_public(request=request, form=form)
