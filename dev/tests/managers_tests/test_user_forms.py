import uuid
from typing import Any, Dict

import pytest
from httpx import AsyncClient

from app.db import UserFormsDb
from app.db.models import User, UserForm
from app.dependencies.exceptions import RequestedDataNotFoundException, PermissionDeniedException
from app.managers import UserFormManager
from app.schemas.user_forms import UserFormCreateSchema, UserFormSchemaWithoutQrcode, UserFormSchemaWithQrcode, \
    UserFormUpdateSchema
from dev.tests.utils import assert_api_contains_orm, assert_http_error

pytestmark = pytest.mark.asyncio

class TestUserFormsSuccess:
    """✅ Success cases."""

    @staticmethod
    async def test_create_form(seeded_db: Dict[str, Any]) -> None:
        get_user: User = seeded_db["user1"]
        data = UserFormCreateSchema(
            title="title",
            description="description",
        )
        expected_data: UserFormSchemaWithoutQrcode = await UserFormManager.create_form(user_id=get_user.id, data=data)
        assert expected_data.title == data.title
        assert expected_data.description == data.description
        assert expected_data.user_id == get_user.id
        assert isinstance(expected_data, UserFormSchemaWithoutQrcode)

    @staticmethod
    async def test_get_one_form(seeded_db: Dict[str, Any]) -> None:
        get_user: User = seeded_db["user1"]
        get_form: UserForm = seeded_db["user1_forms"][0]
        expected_data: UserFormSchemaWithoutQrcode = await UserFormManager.get_form(form_id=get_form.id, user_id=get_user.id)
        assert expected_data.id == get_form.id
        assert expected_data.user_id == get_user.id
        assert expected_data.title == get_form.title
        assert isinstance(expected_data, UserFormSchemaWithoutQrcode)

    @staticmethod
    async def test_get_list_forms(seeded_db: Dict[str, Any]) -> None:
        get_user: User = seeded_db["user1"]

        expected_data: list[UserFormSchemaWithQrcode] = await UserFormManager.get_list(user_id=get_user.id)
        assert len(expected_data) == len(seeded_db["user1_forms"])
        for f in expected_data:
            assert isinstance(f, UserFormSchemaWithQrcode)
        assert_api_contains_orm(
            api_items=[f.model_dump() for f in expected_data],
            orm_items=seeded_db["user1_forms"],
            fields=("id", "title", "description", "user_id"),
        )

    # todo: Сейчас метод возвращает disabled_forms admin, а должен возвращать пользователя конкретного или все формы.
    @staticmethod
    async def test_get_all_disabled_forms(seeded_db: Dict[str, Any]) -> None:
        get_admin: User = seeded_db["admin"]
        expected_data: list[UserFormSchemaWithQrcode] = await UserFormManager.get_all_forms(user_id=get_admin.id)
        assert_api_contains_orm(
            api_items=[f.model_dump() for f in expected_data],
            orm_items=seeded_db["user1_forms"],
            fields=("id", "title", "description", "user_id"),
        )
        for f in expected_data:
            assert isinstance(f, UserFormSchemaWithQrcode)

    @staticmethod
    async def test_update_form(seeded_db: Dict[str, Any]) -> None:
        get_user: User = seeded_db["user1"]
        get_form: UserForm = seeded_db["user1_forms"][0]
        data = UserFormUpdateSchema(
            title="New Title"
        )
        expected_data: UserFormSchemaWithoutQrcode = await UserFormManager.update_form(form_id=get_form.id, user_id=get_user.id,
                                                                                data=data)
        assert expected_data.title == data.title
        assert expected_data.description == get_form.description
        assert isinstance(expected_data, UserFormSchemaWithoutQrcode)

    @staticmethod
    async def test_delete_form(seeded_db: Dict[str, Any]) -> None:
        get_user: User = seeded_db["user1"]
        get_form: UserForm = seeded_db["user1_forms"][0]
        expected_data: UserFormSchemaWithoutQrcode = await UserFormManager.delete_form(form_id=get_form.id, user_id=get_user.id)
        assert expected_data.id == get_form.id
        assert expected_data.user_id == get_user.id
        assert isinstance(expected_data, UserFormSchemaWithoutQrcode)

    @staticmethod
    async def test_get_public_form_success(seeded_db: Dict[str, Any]) -> None:
        form = seeded_db["user1_forms"][0]

        expected_data: UserFormSchemaWithoutQrcode = await UserFormManager.get_public_form(form_id=form.id)

        assert isinstance(expected_data, UserFormSchemaWithoutQrcode)
        assert expected_data.id == form.id
        assert expected_data.title == form.title
        assert expected_data.description == form.description
        assert expected_data.user_id == form.user_id

    @staticmethod
    async def test_get_qrcode_success(seeded_db) -> None:
        get_form: UserForm = seeded_db["user1_forms"][0]

        expected: bytes = b"fake-png-bytes"
        await UserFormsDb().set_qrcode(form_id=get_form.id, qrcode=expected)

        expected_data = await UserFormManager.get_qrcode(form_id=get_form.id)

        assert isinstance(expected_data, (bytes, bytearray))
        assert expected_data == expected

class TestUserFormsErrors:
    """❌ Error cases."""
    class TestNotFound:
        """404-like errors: RequestedDataNotFoundException"""

        @staticmethod
        async def test_get_form_not_found(seeded_db: Dict[str, Any]) -> None:
            get_user: User = seeded_db["user1"]
            error_id = uuid.uuid4()
            with pytest.raises(RequestedDataNotFoundException, match="Form not found"):
                await UserFormManager.get_form(form_id=error_id, user_id=get_user.id)

        @staticmethod
        async def test_update_form_not_found(seeded_db: Dict[str, Any]) -> None:
            get_user: User = seeded_db["user1"]
            error_id = uuid.uuid4()
            data = UserFormUpdateSchema(title="New Title")
            with pytest.raises(RequestedDataNotFoundException, match="Form not found"):
                await UserFormManager.update_form(form_id=error_id, user_id=get_user.id, data=data)

        @staticmethod
        async def test_delete_form_not_found(seeded_db: Dict[str, Any]) -> None:
            get_user: User = seeded_db["user1"]
            error_id = uuid.uuid4()
            with pytest.raises(RequestedDataNotFoundException, match="Form not found"):
                await UserFormManager.delete_form(form_id=error_id, user_id=get_user.id)

        @staticmethod
        async def test_get_public_form_not_found(seeded_db: Dict[str, Any]) -> None:
            missing_id = uuid.uuid4()
            with pytest.raises(RequestedDataNotFoundException, match="Form not found"):
                await UserFormManager.get_public_form(form_id=missing_id)

        @staticmethod
        async def test_get_qrcode_form_not_found() -> None:
            missing_id = uuid.uuid4()
            with pytest.raises(RequestedDataNotFoundException, match="Form not found"):
                await UserFormManager.get_qrcode(form_id=missing_id)

    class TestPermissionDenied:
        """403-like errors: PermissionDeniedException"""

        @staticmethod
        async def test_get_form_permission_denied(seeded_db: Dict[str, Any]) -> None:
            get_user: User = seeded_db["user2"]
            alien_form: UserForm = seeded_db["user1_forms"][0]
            with pytest.raises(PermissionDeniedException, match="You have no access to this form"):
                await UserFormManager.get_form(form_id=alien_form.id, user_id=get_user.id)

        @staticmethod
        async def test_update_form_permission_denied(seeded_db: Dict[str, Any]) -> None:
            get_user: User = seeded_db["user2"]
            alien_form: UserForm = seeded_db["user1_forms"][0]
            data = UserFormUpdateSchema(title="New Title")
            with pytest.raises(PermissionDeniedException, match="You have no access to this form"):
                await UserFormManager.update_form(form_id=alien_form.id, user_id=get_user.id, data=data)

        @staticmethod
        async def test_delete_form_permission_denied(seeded_db: Dict[str, Any]) -> None:
            get_user: User = seeded_db["user2"]
            alien_form: UserForm = seeded_db["user1_forms"][0]
            with pytest.raises(PermissionDeniedException, match="You have no access to this form"):
                await UserFormManager.delete_form(form_id=alien_form.id, user_id=get_user.id)
