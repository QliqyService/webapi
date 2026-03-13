from fastapi import File, UploadFile, status
from fastapi.responses import StreamingResponse

from app.dependencies.http import AccessTokenDepends, ActiveUserDepends
from app.managers import Managers
from app.routers.api.base import Router
from app.schemas.users.users import (
    UserSchema,
    UserUpdateSchema,
)


router = Router(
    name="Users",
    description="Operations on users for themselves",
)


@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=UserSchema,
)
async def get_me(
    user: ActiveUserDepends,
):
    """
    Get current user.

    ### Output
    - **id**: user ID
    - **email**: user email
    - **first_name**: user first name
    - **last_name**: user last name
    """
    return await Managers.users.get_me(user_id=user.id)


@router.patch(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=UserSchema,
)
async def update_me(
    user_data: UserUpdateSchema,
    user: ActiveUserDepends,
    access_token: AccessTokenDepends,
):
    """
    Update current user.

    ### Input
    - **email**: user email
    - **first_name**: user first name
    - **last_name**: user last name

    ### Output
    - **id**: user ID
    - **email**: user email
    - **first_name**: user first name
    - **last_name**: user last name
    """
    return await Managers.users.update_me(
        user_id=user.id,
        user_data=user_data,
        access_token=access_token,
    )

@router.get(
    "/my_code",
    status_code=status.HTTP_200_OK,
    response_model=UserSchema,
)
async def find_my_code(
    user: ActiveUserDepends,
):
    """
    Get code of user.

    ### Output
    - **code**: user Code for account linking
    """
    code = await Managers.users.get_me(user_id=user.id)
    return code.usercode
@router.post(
    "/me/avatar",
    status_code=status.HTTP_200_OK,
)

async def upload_my_avatar(
    user: ActiveUserDepends,
    file: UploadFile = File(...),
):
    """
    Upload avatar for current user.

    Input: multipart/form-data with field `file`
    Output: {"avatar_key": "..."}
    """
    return await Managers.users.upload_avatar(user_id=user.id, file=file)

@router.get(
    "/me/avatar",
    status_code=status.HTTP_200_OK,
)
async def get_my_avatar(
    user: ActiveUserDepends,
):
    avatar = await Managers.users.get_avatar(user_id=user.id)

    return StreamingResponse(
        avatar["body"],
        media_type=avatar["content_type"],
        headers={
            "Content-Disposition": f'inline; filename="{avatar["filename"]}"',
            **(
                {"Content-Length": str(avatar["content_length"])}
                if avatar["content_length"] is not None
                else {}
            ),
        },
    )
