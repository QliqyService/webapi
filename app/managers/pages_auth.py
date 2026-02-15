from fastapi import Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.managers import Managers
from app.views.private_page import user_forms as page_views


class PagesAuthManager:
    COOKIE_NAME = "access_token"
    COOKIE_MAX_AGE = 60 * 60 * 24 * 14

    @staticmethod
    async def login_page(request: Request) -> HTMLResponse:
        return page_views.login_page(request)

    @classmethod
    async def login_submit(cls, username: str, password: str) -> RedirectResponse:
        token = await Managers.auth.login(email=username.lower(), password=password)

        resp = RedirectResponse(url="forms", status_code=303)
        resp.set_cookie(
            key=cls.COOKIE_NAME,
            value=token.access_token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=cls.COOKIE_MAX_AGE,
            path="/",
        )
        return resp

    @classmethod
    async def logout_submit(cls) -> RedirectResponse:
        resp = RedirectResponse(url="forms", status_code=303)
        resp.delete_cookie(key=cls.COOKIE_NAME, path="/")
        return resp
