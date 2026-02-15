import pytest_asyncio
from sqlalchemy import delete

from app.services import Services
from app.db.models.users import User


@pytest_asyncio.fixture
async def started_db():
    await Services.database.start()
    yield
    await Services.database.stop()

@pytest_asyncio.fixture
async def clean_db(started_db):
    async with Services.database.session() as session:
        await session.execute(delete(User))
        await session.commit()
    yield