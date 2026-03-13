from faststream.rabbit.fastapi import RabbitRouter
from loguru import logger as LOGGER

from app.routers.streaming.account_linking import router
from app.settings import SETTINGS


__all__ = ["account_linking_router"]


account_linking_router = RabbitRouter(url=SETTINGS.RABBITMQ_URL)
account_linking_router.include_router(router)
LOGGER.debug("✅ account_linking_router was included")
