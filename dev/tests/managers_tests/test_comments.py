import uuid
from typing import Any, Dict

import pytest

from app.dependencies.exceptions import RequestedDataNotFoundException
from app.managers.comments import CommentsManager
from app.schemas.comments.comments import CommentsCreateSchema, CommentsSchema, CommentsUpdateSchema

pytestmark = pytest.mark.asyncio


class TestCommentsSuccess:
    """✅ Success cases."""

    @staticmethod
    async def test_create_comment(seeded_db: Dict[str, Any]) -> None:
        get_form = seeded_db["user1_forms"][0]

        data = CommentsCreateSchema(
            first_name="John",
            last_name="Doe",
            phone=9876543210,
            title="My title",
            description="My description",
        )

        expected_data: CommentsSchema = await CommentsManager.create(
            user_form_id=get_form.id,
            comment_data=data,
        )

        assert isinstance(expected_data, CommentsSchema)
        assert expected_data.id is not None

        assert expected_data.first_name == data.first_name
        assert expected_data.last_name == data.last_name
        assert expected_data.phone == data.phone
        assert expected_data.title == data.title
        assert expected_data.description == data.description

    @staticmethod
    async def test_get_comment_by_id(seeded_db: Dict[str, Any]) -> None:
        data = seeded_db["user1_comments"][0]

        expected_data: CommentsSchema = await CommentsManager.get_comment(comment_id=data.id)

        assert isinstance(expected_data, CommentsSchema)

        assert expected_data.id == data.id
        assert expected_data.first_name == data.first_name
        assert expected_data.last_name == data.last_name
        assert expected_data.phone == data.phone
        assert expected_data.title == data.title
        assert expected_data.description == data.description

    @staticmethod
    async def test_get_comments_list_for_form(seeded_db: Dict[str, Any]) -> None:
        get_form = seeded_db["user1_forms"][0]

        expected_data: list[CommentsSchema] = await CommentsManager.get_list(user_form_id=get_form.id)

        for c in expected_data:
            assert isinstance(c, CommentsSchema)

        data = [
            c for c in seeded_db["user1_comments"]
            if c.user_form_id == get_form.id
        ]

        assert len(expected_data) == len(data)

        assert {c.id for c in expected_data} == {c.id for c in data}

    @staticmethod
    async def test_update_comment(seeded_db: Dict[str, Any]) -> None:
        get_comment = seeded_db["user1_comments"][0]

        data = CommentsUpdateSchema(
            first_name="Ann",
            last_name="Smith",
            phone=1234567890,
            title="Updated title",
            description="Updated description",
        )

        expected_data: CommentsSchema = await CommentsManager.update(
            comment_id=get_comment.id,
            comment_data=data,
        )

        assert isinstance(expected_data, CommentsSchema)
        assert expected_data.id == get_comment.id

        assert expected_data.first_name == data.first_name
        assert expected_data.last_name == data.last_name
        assert expected_data.phone == data.phone
        assert expected_data.title == data.title
        assert expected_data.description == data.description

    @staticmethod
    async def test_delete_comment(seeded_db: Dict[str, Any]) -> None:
        data = seeded_db["user1_comments"][0]

        expected_data: CommentsSchema = await CommentsManager.delete(comment_id=data.id)

        assert isinstance(expected_data, CommentsSchema)

        assert expected_data.id == data.id

        with pytest.raises(RequestedDataNotFoundException, match="Comment not found"):
            await CommentsManager.get_comment(comment_id=data.id)


class TestCommentsErrors:
    """❌ Error cases."""

    class TestNotFound:
        """404-like errors: RequestedDataNotFoundException"""

        @staticmethod
        async def test_get_comment_not_found() -> None:
            missing_id = uuid.uuid4()
            with pytest.raises(RequestedDataNotFoundException, match="Comment not found"):
                await CommentsManager.get_comment(comment_id=missing_id)

        @staticmethod
        async def test_update_comment_not_found() -> None:
            missing_id = uuid.uuid4()
            data = CommentsUpdateSchema(title="New", description="New")
            with pytest.raises(RequestedDataNotFoundException, match="Comment not found"):
                await CommentsManager.update(comment_id=missing_id, comment_data=data)

        @staticmethod
        async def test_delete_comment_not_found() -> None:
            missing_id = uuid.uuid4()
            with pytest.raises(RequestedDataNotFoundException, match="Comment not found"):
                await CommentsManager.delete(comment_id=missing_id)
