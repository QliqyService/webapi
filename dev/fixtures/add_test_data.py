import pytest
from sqlalchemy import delete

from app.services import Services
from app.db.models import User, UserForm, Comment

from dev.factories import UserFactory, UserFormFactory, CommentFactory
from dev.fixtures.db import started_db

@pytest.fixture
async def seeded_db(started_db):
    async with Services.database.session() as session:
        await session.execute(delete(User))

        user1: User = UserFactory.build(email="seed.user1@example.com", is_superuser=False, is_verified=True)
        user2: User = UserFactory.build(email="seed.user2@example.com", is_superuser=False, is_verified=True)
        admin: User = UserFactory.build(email="seed.admin@example.com", is_superuser=True, is_verified=True)

        session.add_all([user1, user2, admin])
        await session.flush()

        forms: list[UserForm] = []
        comments: list[Comment] = []
        for u in (user1, user2):
            for _ in range(2):
                form = UserFormFactory.build(user_id=u.id)
                session.add(form)
                await session.flush()
                forms.append(form)

                built_comments = [CommentFactory.build(user_form_id=form.id) for _ in range(2)]
                session.add_all(built_comments)
                comments.extend(built_comments)

        await session.commit()

    user1_forms = [f for f in forms if f.user_id == user1.id]
    user2_forms = [f for f in forms if f.user_id == user2.id]
    user1_form_ids = {f.id for f in user1_forms}
    user2_form_ids = {f.id for f in user2_forms}
    user1_comments = [c for c in comments if c.user_form_id in user1_form_ids]
    user2_comments = [c for c in comments if c.user_form_id in user2_form_ids]

    return {
        "user1": user1,
        "user2": user2,
        "admin": admin,
        "forms": forms,
        "user1_forms": user1_forms,
        "user2_forms": user2_forms,
        "comments": comments,
        "user1_comments": user1_comments,
        "user2_comments": user2_comments,
    }
