from __future__ import annotations

from typing import Any, Dict

import pytest
from httpx import AsyncClient

from dev.tests.utils import assert_http_error

pytestmark = pytest.mark.asyncio

def payload_create_comment(**overrides: Any) -> dict[str, Any]:
    data: dict[str, Any] = {
        "first_name": "Ilya",
        "last_name": "Ivanov",
        "phone": 123456789,
        "title": "Hello",
        "description": "My comment text",
    }
    data.update(overrides)
    return data


INVALID_CREATE_PAYLOADS: list[dict[str, Any]] = [
    payload_create_comment(title=None),
    payload_create_comment(description=None),
    payload_create_comment(phone=None),
    payload_create_comment(title=""),
    payload_create_comment(title="x" * 129),
    payload_create_comment(description="x" * 1025),
    payload_create_comment(phone="abc"),
]

INVALID_UPDATE_PAYLOADS: list[dict[str, Any]] = [
    {"title": 123},
    {"description": 123},
    {"title": "x" * 129},
    {"description": "x" * 1025},
    {"phone": "abc"},
]

class TestCommentsSuccess:
    """✅ Success cases."""
    @staticmethod
    async def test_create_comment(
        api_anon_client: AsyncClient,
        seeded_db: Dict[str, Any],
    ) -> None:
        expected_data = next(f for f in seeded_db["user1_forms"] if f.is_enabled)

        payload = payload_create_comment()

        resp = await api_anon_client.post(
            f"/comments/forms/{expected_data.id}/comments",
            json=payload,
        )
        assert resp.status_code == 201, resp.text

        data = resp.json()
        assert data["title"] == payload["title"]
        assert data["description"] == payload["description"]
        assert data["first_name"] == payload["first_name"]
        assert data["last_name"] == payload["last_name"]
        assert data["phone"] == payload["phone"]

        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
    @staticmethod
    async def test_get_comment_by_id(
        api_anon_client: AsyncClient,
        seeded_db: Dict[str, Any],
    ) -> None:
        expected_data = next(f for f in seeded_db["user1_forms"] if f.is_enabled)

        created = await api_anon_client.post(
            f"/comments/forms/{expected_data.id}/comments",
            json=payload_create_comment(title="T1", description="D1"),
        )
        assert created.status_code == 201, created.text
        comment_id = created.json()["id"]

        resp = await api_anon_client.get(f"/comments/comments/{comment_id}")
        assert resp.status_code == 200, resp.text

        data = resp.json()
        assert data["id"] == comment_id
        assert data["title"] == "T1"
        assert data["description"] == "D1"
        assert data["phone"] == 123456789
        assert data["first_name"] == "Ilya"
        assert data["last_name"] == "Ivanov"

    @staticmethod
    async def test_get_comments_list_for_form(
        api_client: AsyncClient,
        api_anon_client: AsyncClient,
        seeded_db: Dict[str, Any],
    ) -> None:
        expected_data = next(f for f in seeded_db["user1_forms"] if f.is_enabled)

        for i in range(2):
            r = await api_anon_client.post(
                f"/comments/forms/{expected_data.id}/comments",
                json=payload_create_comment(title=f"T{i}", description=f"D{i}"),
            )
            assert r.status_code == 201, r.text

        resp = await api_client.get(f"/comments/forms/{expected_data.id}/comments")
        assert resp.status_code == 200, resp.text

        data = resp.json()
        assert isinstance(data, list)
        assert len(data) >= 2

        for item in data:
            assert "id" in item
            assert "first_name" in item
            assert "last_name" in item
            assert "title" in item
            assert "description" in item
            assert "phone" in item
            assert "created_at" in item
            assert "updated_at" in item

        assert data[0]["created_at"] >= data[-1]["created_at"]


class TestCommentsErrors:
    """❌ Error cases."""

    class TestUnauthorized:
        """🔒 Unauthorized/Forbidden."""

        @staticmethod
        async def test_get_comments_list(
            api_anon_client: AsyncClient,
            seeded_db: Dict[str, Any],
        ) -> None:
            expected_data = next(f for f in seeded_db["user1_forms"] if f.is_enabled)

            resp = await api_anon_client.get(f"/comments/forms/{expected_data.id}/comments")
            assert_http_error(resp, 401, "Access token is missing")

    class TestValidation:
        """🧪 Validation errors."""

        @staticmethod
        @pytest.mark.parametrize("payload", INVALID_CREATE_PAYLOADS)
        async def test_create_comment_invalid_payload(
            api_anon_client: AsyncClient,
            seeded_db: Dict[str, Any],
            payload: dict[str, Any],
        ) -> None:
            expected_data = next(f for f in seeded_db["user1_forms"] if f.is_enabled)

            resp = await api_anon_client.post(
                f"/comments/forms/{expected_data.id}/comments",
                json=payload,
            )
            assert resp.status_code in (400, 422), resp.text

        @staticmethod
        @pytest.mark.parametrize("payload", INVALID_UPDATE_PAYLOADS)
        async def test_update_comment_invalid_payload(
            api_anon_client: AsyncClient,
            seeded_db: Dict[str, Any],
            payload: dict[str, Any],
        ) -> None:
            expected_data = next(f for f in seeded_db["user1_forms"] if f.is_enabled)

            created = await api_anon_client.post(
                f"/comments/forms/{expected_data.id}/comments",
                json=payload_create_comment(title="T", description="D"),
            )
            assert created.status_code == 201, created.text
            comment_id = created.json()["id"]

            resp = await api_anon_client.patch(
                f"/comments/comment/{comment_id}",
                json=payload,
            )
            assert resp.status_code in (400, 422), resp.text
