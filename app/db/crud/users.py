from uuid import UUID

import sqlalchemy.orm as so
from sqlalchemy import delete, exists, select, update

from app.db.crud.base import BaseDatabase
from app.db.models.users import User
from app.schemas.users.users import UserSchema, UserUpdateSchema
from app.services import Services


class UsersDb(BaseDatabase):
    """CRUD operations for users."""

    @staticmethod
    async def create(user: UserSchema) -> UserSchema:
        """Create user.

        Args:
            user (UserSchema): user model

        Returns:
            UserSchema: created user model
        """
        data = user.model_dump()

        user_db = User(**data)
        async with Services.database.session() as session:
            session.add(user_db)
        return UserSchema.model_validate(user_db)

    @staticmethod
    async def get(user_id: UUID) -> UserSchema | None:
        """Get user by id.

        Args:
            user_id (UUID): user ID

        Returns:
            UserSchema | None: user if found, None otherwise
        """
        query = select(User).where(User.id == user_id)
        async with Services.database.session() as session:
            result = await session.execute(query)
        user_db = result.scalar()
        if not user_db:
            return None
        return UserSchema.model_validate(user_db)

    @staticmethod
    async def update(user_id: UUID, user_data: UserUpdateSchema) -> UserSchema:
        """Update user.

        Args:
            user_id (UUID): ID of the user
            user_data (UserUpdateSchema): data of the user to update

        Returns:
            UserSchema: updated user
        """
        data = user_data.model_dump(exclude_unset=True)

        async with Services.database.session() as session:
            result = await session.execute(update(User).where(User.id == user_id).values(**data).returning(User))
        user_db = result.scalar()

        return UserSchema.model_validate(user_db)

    @staticmethod
    async def delete(user_id: UUID) -> UserSchema | None:
        """Delete user by its ID.

        Args:
            user_id (UUID): user ID

        Returns:
            UserSchema | None: user if found, None otherwise
        """
        query = delete(User).where(User.id == user_id).returning(User)
        async with Services.database.session() as session:
            result = await session.execute(query)
        user_db = result.scalar()
        if not user_db:
            return None
        return UserSchema.model_validate(user_db)

    @staticmethod
    async def exists_by_email(email: str) -> bool:
        """Check if user exists by email.

        Args:
            email (str): user email

        Returns:
            bool: True if user exists, False otherwise
        """
        query = exists(User).where(User.email == email).select()
        async with Services.database.session() as session:
            result = await session.execute(query)
        return bool(result.scalar())

    @staticmethod
    async def exists_by_id(user_id: UUID) -> bool:
        """Check if user exists by ID

        Args:
            user_id (UUID): user ID

        Returns:
            bool: True if user exists, False otherwise
        """
        query = exists(User).where(User.id == user_id).select()
        async with Services.database.session() as session:
            result = await session.execute(query)
        return bool(result.scalar())

    @staticmethod
    async def exists_by_phone(phone: int) -> bool:
        """Check if user exists by phone.

        Args:
            phone (int): user phone

        Returns:
            bool: True if user exists, False otherwise
        """
        query = exists(User).where(User.phone == phone).select()
        async with Services.database.session() as session:
            result = await session.execute(query)
        return bool(result.scalar())

    @staticmethod
    async def get_by_email(email: str) -> UserSchema | None:
        """Get user by email.

        Args:
            email (str): user email

        Returns:
            UserSchema | None: user model if found, None otherwise
        """
        email = str(email).strip().lower()
        query = select(User).where(User.email == email)
        async with Services.database.session() as session:
            result = await session.execute(query)
        user_db = result.scalar()
        if not user_db:
            return None
        return UserSchema.model_validate(user_db)

    @staticmethod
    async def get_by_pk(pk: UUID) -> UserSchema | None:
        """Get user by email.

        Args:
            pk (UUID): user pk

        Returns:
            UserSchema | None: user model if found, None otherwise
        """
        query = (
            select(User)
            .options(
                so.load_only(
                    User.id,
                    User.email,
                    User.phone,
                    User.first_name,
                    User.last_name,
                    User.is_active,
                    User.is_superuser,
                    User.is_verified,
                    User.created_at,
                    User.updated_at,
                )
            )
            .where(User.id == pk)
        )
        async with Services.database.session() as session:
            result = await session.execute(query)
        user_db = result.scalar()
        if not user_db:
            return None
        return UserSchema.model_validate(user_db)

    @staticmethod
    async def get_list() -> list[UserSchema]:
        """Get list of all users.

        Returns:
            list[UserSchema]: list of users
        """
        query = select(User)
        async with Services.database.session() as session:
            result = await session.execute(query)
        users_db = result.fetchall()
        return [(UserSchema.model_validate(user_db)) for user_db in users_db]

    @staticmethod
    async def update_verified(user_id: UUID, is_verified: bool) -> UserSchema:
        async with Services.database.session() as session:
            result = await session.execute(
                (
                    update(User)
                    .where(
                        User.id == user_id,
                    )
                    .values(
                        is_verified=is_verified,
                    )
                    .returning(User)
                )
            )
        user_db = result.scalar()
        return UserSchema.model_validate(user_db)
