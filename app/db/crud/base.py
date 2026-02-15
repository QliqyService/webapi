import time
from contextlib import asynccontextmanager
from enum import StrEnum
from functools import wraps
from typing import Any, AsyncGenerator, Awaitable, Callable, ParamSpec, Sequence, TypeVar

import sqlalchemy as sa
from loguru import logger as LOGGER
from pydantic import BaseModel, TypeAdapter
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.asyncio import AsyncSession

from app.services import Services
from app.services.postgresql import SQLAlchemyBase


__all__ = [
    "BaseDatabase",
    "SortOrder",
    "sqlalchemy_to_pydantic",
    "PSQL_QUERY_ALLOWED_MAX_ARGS",
    "db_session_handler",
]

PSQL_QUERY_ALLOWED_MAX_ARGS = 32767


class SortOrder(StrEnum):
    ASC = "asc"
    DESC = "desc"


T = TypeVar("T")
P = ParamSpec("P")


def db_session_handler(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
    """Decorator to handle database session management for async functions.

    Args:
        func (Callable[[Any, Any], Awaitable[Any]]): The async function to be wrapped.

    Returns:
        Callable[[Any, Any], Awaitable[Any]]: The wrapped function that manages the session.
    """

    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        """Wrapper function that manages the database session.

        Args:
            *args: Positional arguments passed to the wrapped function.
            **kwargs: Keyword arguments passed to the wrapped function, including an optional 'session'.

        Returns:
            T: The result of the wrapped function.
        """

        if session := kwargs.pop("session", None):
            assert isinstance(session, AsyncSession)

            kwargs["session"] = session
            result = await func(*args, **kwargs)

        else:
            async with Services.database.session() as session:
                kwargs["session"] = session
                result = await func(*args, **kwargs)

        return result

    return wrapper


class BaseDatabase:
    @asynccontextmanager
    async def _profiled_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Контекстный менеджер для сессии с профилированием SQL запросов"""
        start_time = time.time()
        async with Services.database.session() as session:
            # Сохраняем оригинальный метод execute
            original_execute = session.execute

            async def profiled_execute(query, *args, **kwargs):
                # Компилируем запрос в SQL строку
                sql = str(query.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True}))
                LOGGER.debug(f"SQL Query:\n{sql}")

                # Выполняем оригинальный запрос
                query_start = time.time()
                result = await original_execute(query, *args, **kwargs)
                query_time = time.time() - query_start

                LOGGER.debug(f"Query executed in: {query_time:.3f}s")
                return result

            # Подменяем метод execute на профилированную версию
            session.execute = profiled_execute
            try:
                yield session
            finally:
                session_time = time.time() - start_time
                LOGGER.debug(f"SQL session completed in: {session_time:.3f}s")

    @staticmethod
    def set_search_by_column(query: sa.Select, search: str, column: sa.Column) -> sa.Select:
        """
        Setting 'search' variable value as searching by getting SQLAlchemy 'column'.

        Args:
            query: collected user select(...).where(...).
            search: what should be searched for by the selected 'column' in the database.
            column: SQLAlchemy column for searching 'search' inside.
        Returns:
            sa.Select: updated select(...).where(...).where(column.icontains(search)).
        """

        search = search.strip().lower()
        if len(search) != 0:
            query = query.where(column.icontains(search))
        return query

    @staticmethod
    def set_offset_limit(query: sa.Select, offset: int | None, limit: int | None) -> sa.Select:
        """
        Setting 'offset' and 'limit' for collected user select(...).where(...).

        Args:
            query: collected user select(...).where(...).
            offset: used to skip rows before returning a result of the query.
            limit: number of rows returned by the query.
        Returns:
            sa.Select: updated select(...).where(...).offset(offset).limit(limit).
        """
        if limit is None and offset is None:
            return query

        return query.offset(offset).limit(limit)

    @staticmethod
    def set_order_by(query: sa.Select, sort_by: str, sort_order: SortOrder) -> sa.Select:
        """
        Setting 'order_by' with 'asc' and 'desc' options for collected user select(...).where(...).

        Args:
            query: collected user select(...).where(...).
            sort_by: sorting column in database.
            sort_order: option to sort rows in 'sort_order.ASC' or in 'sort_order.DESC' order.
        Returns:
            sa.Select: updated select(...).where(...).order_by("column asc").
        """

        sort_by = sort_by.strip().lower()
        sort_order = sort_order.strip().lower()
        query = query.order_by(sa.text(f"{sort_by} {sort_order}"))
        return query

    async def execute_query(self, query):
        """Выполнение запроса с профилированием"""
        async with self._profiled_session() as session:
            result = await session.execute(query)
            return result


def sqlalchemy_to_pydantic(func):
    """
    Decorator for converting SQLAlchemy model to Pydantic model that
    specified in __annotation__ attribute covering method.
    Checking return type of method and convert to specified type.
    """

    def _as_dict(row: sa.Row) -> dict[str, Any]:
        """
        Function convert sa.Row to linear dictionary view.
        For example, client can request SQLAlchemy User model (id, name) and his tasks count.
        (User(id, name), 10) is one row of query. This method convert this view to dictionary:
        {"id": 1, "name": "Big Brother", "tasks_count": 10}.

        PS. You need to specify key 'tasks_count' when make select(count(...).label('tasks_count')).where(...)
        """
        dict_ = {}
        for k, v in row._asdict().items():
            if issubclass(type(v), SQLAlchemyBase):
                dict_.update(v.to_dict())
            elif v is not None:
                dict_[k] = v
        return dict_

    @wraps(func)
    async def inner(*args, **kwargs) -> list[BaseModel] | BaseModel | None | Sequence[sa.Row]:
        result = await func(*args, **kwargs)
        is_sqlalchemy_response = isinstance(result, sa.ChunkedIteratorResult)
        if "return" not in func.__annotations__ or not is_sqlalchemy_response:
            return result
        result = result.fetchall()

        return_class = func.__annotations__["return"]
        is_list = hasattr(return_class, "__origin__") and isinstance([], return_class.__origin__)

        if len(result) == 0:
            return [] if is_list else None

        result = [_as_dict(r) for r in result]
        return TypeAdapter(return_class).validate_python(result if is_list else result[0])

    return inner
