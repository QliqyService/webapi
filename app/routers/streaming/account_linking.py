from faststream.rabbit import RabbitQueue, RabbitRouter
from loguru import logger as LOGGER
from sqlalchemy import update

from app.db.models.users import User
from app.schemas.account_linking import TGRPCRequest, TGRPCResponse
from app.services import Services
from app.settings import SETTINGS


webapi_prefix = f"{SETTINGS.APP_STAND}::webapi::"
router = RabbitRouter(prefix=webapi_prefix)


@router.subscriber(RabbitQueue(name="link_account"))
async def link_account_handler(payload: TGRPCRequest) -> TGRPCResponse:
    telegram_id = payload.telegram_id
    code = payload.code
    telegram_username = payload.telegram_username
    LOGGER.debug(f"Got a payload from tg user {payload.telegram_id}")
    if not telegram_id or not code:
        return TGRPCResponse(telegram_id=telegram_id or "", code=code or "", ok=str(False))

    try:
        async with Services.database.session() as session:
            await session.execute(
                update(User)
                .where(User.usercode == code)
                .values(
                    tg_account=telegram_id,
                    tg_username=telegram_username,
                    tg_notify_enabled=True,
                )
            )
            await session.commit()
            return TGRPCResponse(telegram_id=str(telegram_id), code=str(code), ok=str(True))
    except Exception as e:
        LOGGER.exception(f"Account linking failed with error {e}")
        return TGRPCResponse(telegram_id=str(telegram_id), code=str(code), ok=str(False))
