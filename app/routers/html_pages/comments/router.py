from uuid import UUID

from fastapi import Form, Request, status
from fastapi.responses import HTMLResponse
from starlette.responses import RedirectResponse

from app.dependencies.http import CurrentFormDepends
from app.managers import Managers
from app.routers.api.base import Router
from app.schemas.comments.comments import CommentsCreateSchema
from app.views.public_page import comments as views


router = Router(name="Comments (HTML)", description="HTMLResponse user_forms")


@router.get(
    "/public/forms/{form_id}/comments/create",
    response_class=HTMLResponse,
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
async def get_create(request: Request):
    """
    Render HTML comment create page.
    """

    return views.create(request=request)


@router.post(
    "/public/forms/{form_id}/comments/create",
    response_class=RedirectResponse,
    status_code=status.HTTP_303_SEE_OTHER,
    include_in_schema=False,
)
async def create(
    user_form: CurrentFormDepends,
    first_name: str | None = Form(default=None, max_length=32),
    last_name: str | None = Form(default=None, max_length=64),
    title: str = Form(..., max_length=128),
    description: str = Form(..., max_length=1024),
    phone: int = Form(...),
):
    """
    Create comment and redirect to comment page.
    """

    data = CommentsCreateSchema(
        first_name=first_name,
        last_name=last_name,
        title=title,
        description=description,
        phone=phone,
    )
    created = await Managers.comments.create(user_form_id=user_form.id, comment_data=data)

    return RedirectResponse(
        url=f"/qliqy/public/forms/{user_form.id}/comments/{created.id}",
        status_code=303,
    )


@router.get("/form/comments", response_class=HTMLResponse, status_code=status.HTTP_200_OK, include_in_schema=False)
async def get_list(request: Request, user_form: CurrentFormDepends):
    """
    Render HTML comments get_list page.
    """
    comments = await Managers.comments.get_list(user_form_id=user_form.id)
    return views.get_list(request=request, comments=comments)


@router.get(
    "/public/forms/{form_id}/comments/{comment_id}",
    response_class=HTMLResponse,
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
async def get_one(request: Request, form_id: UUID, comment_id: UUID):
    comment = await Managers.comments.get_comment(comment_id=comment_id)
    return views.get_one(request=request, comment=comment, form_id=form_id)


# @router.get(
#     "/forms/{form_id}/comments/{comment_id}/edit",
#     response_class=HTMLResponse,
#     include_in_schema=False,
# )
# async def get_update(request: Request, comment_id: UUID):
#     """
#     Render HTML comment edit page.
#     """
#
#     comment = await Managers.comments.get_comment(comment_id=comment_id)
#     return views.update(request=request, comment=comment)
#
#
# @router.post(
#     "/forms/{form_id}/comments/{comment_id}/edit",
#     response_class=RedirectResponse,
#     status_code=status.HTTP_303_SEE_OTHER,
#     include_in_schema=False,
# )
# async def update(
#     request: Request,
#     form_id: UUID,
#     comment_id: UUID,
#     user: CurrentUserDepends,
#     first_name: str | None = Form(default=None, max_length=32),
#     last_name: str | None = Form(default=None, max_length=64),
#     title: str = Form(..., max_length=128),
#     description: str = Form(..., max_length=1024),
#     phone: int = Form(...),
# ):
#     """
#     Update comment and redirect to comment page.
#     """
#     await Managers.user_forms.get_form(form_id=form_id, user_id=user.id)
#
#     data = CommentsUpdateSchema(
#         first_name=first_name,
#         last_name=last_name,
#         title=title,
#         description=description,
#         phone=phone,
#     )
#
#     await Managers.comments.update(comment_id=comment_id, comment_data=data)
#
#     root = get_root(request)
#     return RedirectResponse(url=f"{root}/user_forms/forms/{form_id}/comments/{comment_id}", status_code=303)
#
#
# @router.post(
#     "/forms/{form_id}/comments/{comment_id}/delete",
#     response_class=RedirectResponse,
#     status_code=status.HTTP_303_SEE_OTHER,
#     include_in_schema=False,
# )
# async def delete(
#     request: Request,
#     comment_id: UUID,
#     user_form: CurrentFormDepends,
# ):
#     """
#     Delete comment and redirect to forms list.
#     """
#     await Managers.comments.delete(comment_id=comment_id)
#
#     root = get_root(request)
#     return RedirectResponse(
#         url=f"{root}/public/forms/{user_form.id}",
#         status_code=303,
#     )
