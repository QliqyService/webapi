from typing import Sequence

from fastapi import Request
from fastapi.responses import HTMLResponse

from app.schemas.comments import CommentsSchema
from app.schemas.user_forms import UserFormCreateSchema, UserFormSchemaWithoutQrcode, UserFormSchemaWithQrcode
from app.views.utils import template


def login_page(request: Request) -> HTMLResponse:
    return template(
        request,
        "user_forms/login.html",
        {"title": "Login"},
    )


def get_one(request: Request, form: UserFormSchemaWithoutQrcode, comments: Sequence[CommentsSchema]) -> HTMLResponse:
    return template(
        request,
        "user_forms/get_one.html",
        {"title": "Моя форма", "form": form, "comments": comments},
    )


def create(request: Request) -> HTMLResponse:
    return template(
        request,
        "user_forms/create.html",
        {
            "title": "Создать форму",
            "form": UserFormCreateSchema(title="", description=""),
        },
    )


def update(request: Request, form: UserFormSchemaWithoutQrcode) -> HTMLResponse:
    return template(
        request,
        "user_forms/update.html",
        {
            "title": "Редактирование формы",
            "form": form,
        },
    )


def get_list(request: Request, forms: Sequence[UserFormSchemaWithQrcode]) -> HTMLResponse:
    return template(
        request,
        "user_forms/get_list.html",
        {
            "title": "Мои формы",
            "forms": forms,
        },
    )
