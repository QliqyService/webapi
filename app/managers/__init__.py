from app.managers.auth import AuthManager
from app.managers.comments import CommentsManager
from app.managers.user_forms import UserFormManager
from app.managers.users import UsersManager


class Managers:
    auth: AuthManager = AuthManager()
    user_forms = UserFormManager()
    users = UsersManager()
    comments = CommentsManager()
