from typing import Sequence
from uuid import UUID

from fastapi import Request
from fastapi.responses import HTMLResponse

from app.schemas.comments.comments import CommentsCreateSchema, CommentsSchema
from app.views.utils import template


def get_list(request: Request, comments: Sequence[CommentsSchema]) -> HTMLResponse:
    return template(
        request,
        "comments/list.html",
        {"title": "Комментарии", "comments": comments},
    )


def get_one(request: Request, comment: CommentsSchema, form_id: UUID) -> HTMLResponse:
    return template(
        request,
        "comments/get_one.html",
        {"title": "Комментарий", "comment": comment, "form_id": form_id},
    )


def create(request: Request) -> HTMLResponse:
    comment = CommentsCreateSchema(first_name=None, last_name=None, title="", description="", phone=0)
    return template(
        request,
        "comments/create.html",
        {"title": "Создать комментарий", "comment": comment},
    )


# def update(request: Request, comment: CommentsSchema) -> HTMLResponse:
#     return template(
#         request,
#         "comments/update.html",
#         {"title": "Редактировать комментарий", "comment": comment},
#     )
