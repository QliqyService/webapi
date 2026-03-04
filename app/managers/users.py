from uuid import UUID

from app.db.crud import UsersDb
from app.dependencies.exceptions import ObjectAlreadyExistsException, RequestedDataNotFoundException
from app.schemas.users.users import UserSchema, UserUpdateSchema
from app.services import Services

from fastapi import UploadFile


class UsersManager:
    @staticmethod
    async def get_me(user_id: UUID) -> UserSchema:
        """Get current user.

        Args:
            user_id: ID of the user

        Returns:
            UserSchema: user model
        """
        return await UsersDb.get(user_id=user_id)

    @staticmethod
    async def sync_from_auth_user(auth_user: UserSchema) -> UserSchema:
        """
        Гарантирует, что пользователь из auth существует в локальной БД webapi.
        Если нет – создаёт, если есть – возвращает.
        """
        user_db = await UsersDb.get(user_id=auth_user.id)

        if not user_db:
            created = await UsersDb.create(user=auth_user)
            return created

        return user_db

    @staticmethod
    async def update_me(user_id: UUID, user_data: UserUpdateSchema, access_token: str) -> UserSchema:
        """Update current user.

        Args:
            user_id: ID of the user
            user_data: data of the user to update
            access_token: access token

        Returns:
            UserSchema: updated user model
        """
        user_db = await UsersDb.get(user_id=user_id)
        if not user_db:
            raise RequestedDataNotFoundException("User not found")

        is_update_email = False
        if user_db.email != user_data.email:
            user_email_existing = await UsersDb.exists_by_email(email=user_data.email)
            if user_email_existing:
                raise ObjectAlreadyExistsException("Email already exists")
            is_update_email = True

        if user_data.phone and user_db.phone != user_data.phone:
            user_phone_existing = await UsersDb.exists_by_phone(phone=user_data.phone)
            if user_phone_existing:
                raise ObjectAlreadyExistsException("Phone already exists")

        if is_update_email:
            await Services.auth_proxy.patch_user(
                access_token=access_token,
                user_id=user_id,
                data=dict(
                    email=user_data.email,
                    is_verified=False,
                ),
            )

        updated_user_db = await UsersDb.update(user_id=user_id, user_data=user_data)
        return UserSchema.model_validate(updated_user_db)

    @staticmethod
    async def upload_avatar(*, user_id: UUID, file: UploadFile) -> dict:
        user_db = await UsersDb.get(user_id=user_id)

        if not user_db:
            raise RequestedDataNotFoundException("User not found")

        ext = (file.filename.split(".")[-1] if file.filename and "." in file.filename else "bin")

        key = f"avatars/{user_id}/{uuid4().hex}.{ext}"

        Services.minio.upload_fileobj(
            key=key,
            fileobj=file.file,
            content_type=file.content_type,
        )

        await UsersDb.update(user_id=user_id, user_data={"avatar_key": key})

        return {"avatar_key": key}
