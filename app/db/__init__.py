from app.db.crud import UserFormsDb
from app.db.crud.comments import CommentsDb
from app.db.crud.users import UsersDb


__all__ = ["Database"]


class Database:
    users: UsersDb = UsersDb()
    comments: CommentsDb = CommentsDb()
    user_forms: UserFormsDb = UserFormsDb()
