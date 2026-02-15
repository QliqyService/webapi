from typing import Iterable, Sequence, Any


def assert_api_contains_orm(
    api_items: Iterable[dict],
    orm_items: Iterable[Any],
    *,
    fields: Sequence[str],
) -> None:
    """
    Утвердить, что для каждого объекта ORM существует элемент API,
    с соответствующими значениями для заданных полей.
    - api_items: список словарей из ответа API
    - orm_items: список объектов ORM (UserForm, Comment)
    - fields: поля для сравнения (должны существовать в обоих случаях)
    """
    for orm in orm_items:
        assert any(
            all(
                (str(api.get(field)) if api.get(field) is not None else None)
                ==
                (str(getattr(orm, field)) if getattr(orm, field) is not None else None)
                for field in fields
            )
            for api in api_items
        )

def assert_http_error(resp, status_code: int, message: str | None = None) -> None:
    assert resp.status_code == status_code, resp.text
    if message is not None:
        detail = resp.json().get("detail", "")
        assert message in detail, detail
