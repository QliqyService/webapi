from fastapi import Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse

from app.managers.pages_auth import PagesAuthManager
from app.routers.api.base import Router


router = Router(name="Pages Auth", description="HTML auth user_forms (cookie-based).")


@router.get("/login", response_class=HTMLResponse, status_code=status.HTTP_200_OK, include_in_schema=False)
async def login_page(request: Request):
    """
    Render login page (HTML).
    """
    return await PagesAuthManager.login_page(request)


@router.post("/login", response_class=RedirectResponse, status_code=status.HTTP_303_SEE_OTHER, include_in_schema=False)
async def login_submit(
    username: str = Form(...),
    password: str = Form(...),
):
    """
    Login via HTML form:
    - sets `access_token` cookie
    - redirects to `/api/v1/form/forms`
        ### Input
    - **mail**
    -**password**
    """
    return await PagesAuthManager.login_submit(username=username, password=password)


@router.post("/logout", response_class=RedirectResponse, status_code=status.HTTP_303_SEE_OTHER, include_in_schema=False)
async def logout_submit():
    """
    Logout:
    - deletes `access_token` cookie
    - redirects to `/login`
    """
    return await PagesAuthManager.logout_submit()
