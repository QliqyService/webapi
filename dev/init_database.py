import asyncio

import asyncpg
from loguru import logger as LOGGER
from sqlalchemy import delete

from app.db.models import User
from app.logger import CustomLogger
from app.services import Services
from app.settings import get_settings
from dev.factories import UserFactory, UserFormFactory, CommentFactory


class FixtureManager:
    def __init__(self):
        self.config = get_settings()
        self.logger = CustomLogger.make_logger()

    def get_postgres_dsn(self) -> str:
        """Generate a DSN for connecting to the PostgreSQL database."""
        return "postgresql://{}:{}@{}:{}/postgres".format(
            self.config.POSTGRES_USER,
            self.config.POSTGRES_PASSWORD,
            self.config.POSTGRES_HOST,
            self.config.POSTGRES_PORT,
        )

    async def init_database(self):
        """Create a database with context manager and add permissions to the current user."""
        try:
            async with asyncpg.create_pool(dsn=self.get_postgres_dsn()) as pool:
                async with pool.acquire() as conn:
                    await conn.execute(f"CREATE DATABASE {self.config.POSTGRES_DB}")
                    await conn.execute(
                        f"GRANT ALL PRIVILEGES ON DATABASE {self.config.POSTGRES_DB} TO {self.config.POSTGRES_USER}"
                    )
                    LOGGER.warning(f"Database created '{self.config.POSTGRES_DB}', permissions have been granted.")
        except asyncpg.exceptions.DuplicateDatabaseError:
            LOGGER.warning(f"Database '{self.config.POSTGRES_DB}' already exists.")

    async def drop_database(self):
        """Drop database."""
        try:
            async with asyncpg.create_pool(dsn=self.get_postgres_dsn()) as pool:
                async with pool.acquire() as conn:
                    await conn.execute(f"DROP DATABASE {self.config.POSTGRES_DB}")
                    LOGGER.warning(f"Database dropped '{self.config.POSTGRES_DB}'")
        except Exception as e:
            LOGGER.warning(f"Database '{self.config.POSTGRES_DB}' drop failed: {e}.")

    async def seed_database(self):
        """
        The function completely resets user-related data using the ORM.

        ### Behavior
        - Deletes all users (forms and comments are removed via cascade)
        - Creates **2 test users**
        - Creates **2 forms** for each user
        - Creates **2 comments** for each form

        ### Final database state
        - users: 2
        - user_forms: 4
        - comments: 8

        """
        await Services.database.start()

        async with Services.database.session() as session:
            await session.execute(delete(User))

            users = [
                UserFactory.build(email="seed.user1@example.com"),
                UserFactory.build(email="seed.user2@example.com"),
            ]
            session.add_all(users)
            await session.flush()

            for user in users:
                for _ in range(2):
                    form = UserFormFactory.build(user_id=user.id)
                    session.add(form)
                    await session.flush()

                    session.add_all(
                        CommentFactory.build(user_form_id=form.id)
                        for _ in range(2)
                    )

def main_init() -> None:
    app = FixtureManager()
    asyncio.run(app.init_database())


def main_seed() -> None:
    app = FixtureManager()
    asyncio.run(app.seed_database())


def main_drop() -> None:
    app = FixtureManager()
    asyncio.run(app.drop_database())
