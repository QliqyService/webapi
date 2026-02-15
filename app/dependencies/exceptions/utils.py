from typing import NoReturn

from fastapi import HTTPException


def raise_http_exception(
    status_code: int,
    code: int,
    reason: str,
    data: dict | None = None,
) -> NoReturn:
    detail = dict(
        code=code,
        reason=reason,
    )
    if data:
        prepared_data = dict()
        for key, value in data.items():
            if hasattr(value, "hex"):
                prepared_data[key] = str(value)
                continue
            prepared_data[key] = value

        detail["data"] = prepared_data

    raise HTTPException(
        status_code=status_code,
        detail=detail,
    )
