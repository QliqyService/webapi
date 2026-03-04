from fastapi import status

from app.dependencies.http import AccessTokenDepends, ActiveUserDepends
from app.managers import Managers
from app.routers.api.base import Router
from app.schemas.users.users import (
    UserSchema,
    UserUpdateSchema,
)

from fastapi import status, UploadFile, File


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
    file: UploadFile = File(...),
    user: ActiveUserDepends = None,
):
    """
    Upload avatar for current user.

    Input: multipart/form-data with field `file`
    Output: {"avatar_key": "..."}
    """
    return await Managers.users.upload_avatar(user_id=user.id, file=file)
