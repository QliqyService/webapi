from uuid import UUID

from fastapi import status

from app.dependencies.http import CurrentFormDepends, PublicFormDepends
from app.managers.comments import CommentsManager
from app.routers.api.base import Router
from app.schemas.comments.comments import CommentsCreateSchema, CommentsSchema, CommentsUpdateSchema


router = Router(
    name="Comment",
    description="""
API for managing created comments to form.
""",
)


@router.post("/forms/{form_id}/comments", status_code=status.HTTP_201_CREATED, response_model=CommentsSchema)
async def created_comment(
    data: CommentsCreateSchema,
    current_form: PublicFormDepends,
) -> CommentsSchema:
    """
    Create a new comment for the current form.

    ### Input
    - **first_name**: Optional[max 32 chars]
    - **last_name**: Optional[max 64 chars]
    - **title**: [max 128 chars]
    - **description**: [max 1024 chars]
    - **phone**: Optional[max 16 chars]


    ### Output
    - **created_at**: creation datetime
    - **updated_at**: last update datetime
    - **id**: comment UUID
    - **first_name**: user first_name
    - **last_name**: user last_name
    - **title**: comment title
    - **description**: comment description
    - **phone**: user phone
    """
    return await CommentsManager.create(user_form_id=current_form.id, comment_data=data)


@router.get("/comments/{comment_id}", status_code=status.HTTP_200_OK, response_model=CommentsSchema)
async def get_comment(comment_id: UUID) -> CommentsSchema:
    """
    Get current comment by form id.

    ### Input
    - **comment_id** : UUID


    ### Output
    - **created_at**: creation datetime
    - **updated_at**: last update datetime
    - **id**: comment UUID
    - **first_name**: user first_name
    - **last_name**: user last_name
    - **title**: comment title
    - **description**: comment description
    - **phone**: user phone
    """

    return await CommentsManager.get_comment(comment_id=comment_id)


@router.get("/forms/{form_id}/comments", status_code=status.HTTP_200_OK, response_model=list[CommentsSchema])
async def get_list(
    current_form: CurrentFormDepends,
) -> list[CommentsSchema]:
    """
    Get current comments by form id.

    ### Input
    - **form_id** : UUID

    For each comment
    ### Output
    - **created_at**: creation datetime
    - **updated_at**: last update datetime
    - **id**: comment UUID
    - **first_name**: user first_name
    - **last_name**: user last_name
    - **title**: comment title
    - **description**: comment description
    - **phone**: user phone
    """
    return await CommentsManager.get_list(user_form_id=current_form.id)


@router.patch("/comment/{comment_id}", status_code=status.HTTP_200_OK, response_model=CommentsSchema)
async def update_comment(
    data: CommentsUpdateSchema,
    comment_id: UUID,
) -> CommentsSchema:
    """
    Update current comment by form id.

    ### Input
    - **form_id** : UUID

    ### Output
    - **created_at**: creation datetime
    - **updated_at**: last update datetime
    - **id**: comment UUID
    - **first_name**: user first_name
    - **last_name**: user last_name
    - **title**: comment title
    - **description**: comment description
    - **phone**: user phone
    """
    return await CommentsManager.update(comment_id=comment_id, comment_data=data)


@router.delete("/comment/{comment_id}", status_code=status.HTTP_200_OK, response_model=CommentsSchema)
async def delete_comment(
    comment_id: UUID,
) -> CommentsSchema:
    """
    Delete current comment by form id.

    ### Input
    - **form_id** : UUID

    ### Output
    - **created_at**: creation datetime
    - **updated_at**: last update datetime
    - **id**: comment UUID
    - **first_name**: user first_name
    - **last_name**: user last_name
    - **title**: comment title
    - **description**: comment description
    - **phone**: user phone
    """
    return await CommentsManager.delete(comment_id=comment_id)
