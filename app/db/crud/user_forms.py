from uuid import UUID

from sqlalchemy import exists, select, update

from app.db.crud.base import BaseDatabase
from app.db.models.user_forms import UserForm
from app.schemas.user_forms import (
    UserFormCreateSchema,
    UserFormSchemaWithoutQrcode,
    UserFormSchemaWithQrcode,
    UserFormUpdateSchema,
)
from app.services import Services


class UserFormsDb(BaseDatabase):
    """CRUD operations for user forms."""

    @staticmethod
    async def create(user_id: UUID, form: UserFormCreateSchema) -> UserFormSchemaWithoutQrcode:
        """Create user form for given user.

        Args:
            user_id (UUID): ID of the user (owner of form)
            form (UserFormCreateSchema): created form

        Returns:
            UserFormSchemaWithoutQrcode: form data
        """
        data = form.model_dump()

        async with Services.database.session() as session:
            form_db = UserForm(user_id=user_id, **data)
            session.add(form_db)
            await session.commit()

        return UserFormSchemaWithoutQrcode.model_validate(form_db, from_attributes=True)

    @staticmethod
    async def get(form_id: UUID) -> UserFormSchemaWithoutQrcode | None:
        """Get form by ID.

        Args:
            form_id (UUID): form ID

        Returns:
            UserFormSchemaWithoutQrcode | None: form if found and enabled, None otherwise
        """
        query = select(UserForm).where(UserForm.id == form_id, UserForm.is_enabled)
        async with Services.database.session() as session:
            result = await session.execute(query)
            form_db = result.scalar_one_or_none()
        if not form_db:
            return None

        return UserFormSchemaWithoutQrcode.model_validate(form_db, from_attributes=True)

    @staticmethod
    async def update(form_id: UUID, form_data: UserFormUpdateSchema) -> UserFormSchemaWithoutQrcode | None:
        """
        Update form.

        Args:
            form_id (UUID): ID of the form
            form_data (UserFormUpdateSchema): data of the form to update

        Returns:
            UserFormSchemaWithoutQrcode | None: updated form if found, None otherwise
        """
        data = form_data.model_dump(exclude_unset=True)

        async with Services.database.session() as session:
            result = await session.execute(
                update(UserForm).where(UserForm.id == form_id).values(**data).returning(UserForm)
            )
            await session.commit()
            form_db = result.scalar_one_or_none()
        if not form_db:
            return None

        return UserFormSchemaWithoutQrcode.model_validate(form_db, from_attributes=True)

    @staticmethod
    async def delete(form_id: UUID) -> UserFormSchemaWithoutQrcode | None:
        """Delete form by its ID.

        Args:
            form_id (UUID): form ID

        Returns:
            UserFormSchemaWithoutQrcode | None: disabled form if found, None otherwise
        """
        async with Services.database.session() as session:
            result = await session.execute(
                update(UserForm).where(UserForm.id == form_id).values(is_enabled=False).returning(UserForm)
            )
            await session.commit()

            form_db = result.scalar_one_or_none()
            if not form_db:
                return None

        return UserFormSchemaWithoutQrcode.model_validate(form_db, from_attributes=True)

    @staticmethod
    async def exists_by_id(form_id: UUID) -> bool:
        """Check if form exists by ID.

        Args:
            form_id (UUID): form ID

        Returns:
            bool: True if form exists (even if disabled), False otherwise
        """
        query = exists(UserForm).where(UserForm.id == form_id).select()
        async with Services.database.session() as session:
            result = await session.execute(query)
        return bool(result.scalar())

    @staticmethod
    async def get_list(user_id: UUID) -> list[UserFormSchemaWithQrcode]:
        """Get list of all forms for given user.

        Args:
            user_id (UUID): user ID

        Returns:
            list[UserFormSchemaWithQrcode]: list of enabled forms
        """
        query = (
            select(UserForm)
            .where(UserForm.user_id == user_id, UserForm.is_enabled)
            .order_by(UserForm.created_at.desc())
        )
        async with Services.database.session() as session:
            result = await session.execute(query)
        forms_db = result.scalars().all()

        return [UserFormSchemaWithQrcode.model_validate(form_db, from_attributes=True) for form_db in forms_db]

    @staticmethod
    async def set_qrcode(form_id: UUID, qrcode: bytes) -> None:
        """Saves QR in to database."""
        async with Services.database.session() as session:
            await session.execute(update(UserForm).where(UserForm.id == form_id).values(qrcode=qrcode))
            await session.commit()

    @staticmethod
    async def get_qrcode(form_id: UUID) -> bytes | None:
        """Gets QR form database (could be None)."""
        query = select(UserForm.qrcode).where(UserForm.id == form_id)
        async with Services.database.session() as session:
            result = await session.execute(query)
        return result.scalar()

    @staticmethod
    async def get_all_user_forms(user_id: UUID) -> list[UserFormSchemaWithQrcode]:
        """Get list of all forms for given user.

        Args:
            user_id (UUID): user ID

        Returns:
            list[UserFormSchemaWithQrcode]: list of all user forms (even disabled ones)
        """
        query = select(UserForm).where(UserForm.user_id == user_id).order_by(UserForm.created_at.desc())
        async with Services.database.session() as session:
            result = await session.execute(query)
        forms_db = result.scalars().all()

        return [UserFormSchemaWithQrcode.model_validate(form_db, from_attributes=True) for form_db in forms_db]
