import uuid
from typing import Any, Dict

import pytest
from httpx import AsyncClient

from dev.tests.utils import assert_api_contains_orm, assert_http_error

pytestmark = pytest.mark.asyncio

class TestUserFormsSuccess:
    """✅ Success cases."""
    @staticmethod
    async def test_get_list_forms(api_client: AsyncClient, seeded_db: Dict[str, Any]) -> None:
        resp = await api_client.get("/form/forms")
        assert resp.status_code == 200, resp.text

        data = resp.json()
        assert isinstance(data, list)

        expected_data = [
            f for f in seeded_db["user1_forms"]
            if f.is_enabled
        ]

        assert_api_contains_orm(
            api_items=data,
            orm_items=expected_data,
            fields=("title", "description", "user_id"),
        )
        assert len(data) == len(expected_data)

    @staticmethod
    async def test_get_one_form(api_client: AsyncClient, seeded_db: Dict[str, Any]) -> None:
        expected_data = next(f for f in seeded_db["user1_forms"] if f.is_enabled)

        resp = await api_client.get(f"/form/forms/{expected_data.id}")
        assert resp.status_code == 200, resp.text

        data = resp.json()
        assert data["title"] == expected_data.title
        assert data["description"] == expected_data.description
        assert data["user_id"] == str(expected_data.user_id)

    @staticmethod
    async def test_create_form(api_client: AsyncClient, seeded_db: Dict[str, Any]) -> None:
        payload = {"title": "My new form", "description": "Form description"}

        resp = await api_client.post("/form/forms", json=payload)
        assert resp.status_code == 201, resp.text

        data = resp.json()
        assert data["title"] == payload["title"]
        assert data["description"] == payload["description"]
        assert data["user_id"] == str(seeded_db["user1"].id)

    @staticmethod
    async def test_update_form(api_client: AsyncClient, seeded_db: Dict[str, Any]) -> None:
        expected_data = next(f for f in seeded_db["user1_forms"] if f.is_enabled)

        payload = {"title": "Updated title"}

        resp = await api_client.patch(f"/form/forms/{expected_data.id}", json=payload)
        assert resp.status_code == 200, resp.text

        data = resp.json()
        assert data["title"] == payload["title"]
        assert data["description"] == expected_data.description
        assert data["user_id"] == str(expected_data.user_id)

    @staticmethod
    async def test_delete_form(api_client: AsyncClient, seeded_db: Dict[str, Any]) -> None:
        expected_data = next(f for f in seeded_db["user1_forms"] if f.is_enabled)

        resp = await api_client.delete(f"/form/forms/{expected_data.id}")
        assert resp.status_code == 200, resp.text

        data = resp.json()
        assert data["id"] == str(expected_data.id)
        assert data["user_id"] == str(expected_data.user_id)
        assert data["title"] == expected_data.title

    @staticmethod
    async def test_get_all_forms_is_disabled(
        api_client: AsyncClient,
        api_superuser_client: AsyncClient,
        seeded_db: Dict[str, Any],
    ) -> None:
        expected_data = next(f for f in seeded_db["user1_forms"] if f.is_enabled)

        resp = await api_client.delete(f"/form/forms/{expected_data.id}")
        assert resp.status_code == 200, resp.text

        resp = await api_superuser_client.get("/form/forms/all")
        assert resp.status_code == 200, resp.text

        data = resp.json()
        assert isinstance(data, list)

        expected_data = [f for f in seeded_db["forms"] if f.user_id == seeded_db["user1"].id]

        assert_api_contains_orm(
            api_items=data,
            orm_items=expected_data,
            fields=("title", "description", "user_id"),
        )
        assert len(data) == len(expected_data)

class TestUserFormsErrors:
    """❌ Error cases."""
    class TestUnauthorized:
        """🔒 Unauthorized/Forbidden."""

        @staticmethod
        async def test_create_without_auth(api_anon_client: AsyncClient) -> None:
            resp = await api_anon_client.post("/form/forms", json={"title": "T", "description": "D"})
            assert_http_error(resp, 401, "Access token is missing")

        @staticmethod
        async def test_get_list_without_auth(api_anon_client: AsyncClient) -> None:
            resp = await api_anon_client.get("/form/forms")
            assert_http_error(resp, 401, "Access token is missing")

        @staticmethod
        async def test_get_all_as_regular_user(api_client: AsyncClient) -> None:
            resp = await api_client.get("/form/forms/all")
            assert_http_error(resp, 401, "Access token is missing")

        @staticmethod
        async def test_get_one_without_auth(api_anon_client: AsyncClient) -> None:
            resp = await api_anon_client.get(f"/form/forms/{uuid.uuid4()}")
            assert_http_error(resp, 401, "Access token is missing")

        @staticmethod
        async def test_update_without_auth(api_anon_client: AsyncClient) -> None:
            resp = await api_anon_client.patch(f"/form/forms/{uuid.uuid4()}", json={"title": "T"})
            assert_http_error(resp, 401, "Access token is missing")

        @staticmethod
        async def test_get_all_without_auth(api_anon_client: AsyncClient) -> None:
            resp = await api_anon_client.get("/form/forms/all")
            assert_http_error(resp, 401, "Access token is missing")

        @staticmethod
        async def test_delete_without_auth(api_anon_client: AsyncClient) -> None:
            resp = await api_anon_client.delete(f"/form/forms/{uuid.uuid4()}")
            assert_http_error(resp, 401, "Access token is missing")
    class TestValidation:
        """🧪 Validation errors."""

        @staticmethod
        @pytest.mark.parametrize(
            "payload",
            [
                {"title": 123, "description": "ok"},
                {"title": "ok", "description": 123},
                {"description": "only desc"},
                {"title": None, "description": "ok"},
                {"title": "", "description": "ok"},
                {"title": "x" * 129, "description": "ok"},
                {"title": "ok", "description": "x" * 257},
            ],
        )
        async def test_create_form_invalid_payload_returns_422_or_400(
                api_client: AsyncClient,
                payload,
        ) -> None:
            resp = await api_client.post("/form/forms", json=payload)
            assert resp.status_code in (400, 422), resp.text

        @staticmethod
        @pytest.mark.parametrize(
            "payload",
            [
                {"title": 123},
                {"description": 123},
                {"title": ""},
                {"title": "x" * 129},
                {"description": "x" * 257},
            ],
        )
        async def test_update_invalid_payload(api_client: AsyncClient, seeded_db, payload) -> None:
            expected_data = next(
                f for f in seeded_db["forms"]
                if f.user_id == seeded_db["user1"].id and f.is_enabled
            )

            resp = await api_client.patch(f"/form/forms/{expected_data.id}", json=payload)
            assert resp.status_code in (400, 422), resp.text
