from faststream.rabbit import RabbitMessage, RabbitRouter, RabbitQueue
from sqlalchemy import delete, exists, select, update
from app.db.models.users import User
from app.schemas.account_linking import TGRPCRequest, TGRPCResponse
from app.services import Services
from loguru import logger as LOGGER
from app.settings import SETTINGS

webapi_prefix = f"{SETTINGS.APP_STAND}::webapi::"
router = RabbitRouter(prefix=webapi_prefix)


@router.subscriber(RabbitQueue(name="link_account"))
async def link_account_handler(payload: TGRPCRequest) -> TGRPCResponse:
    telegram_id = payload.telegram_id
    code = payload.code
    LOGGER.debug(f"Got a payload from tg user {payload.telegram_id}")
    if not telegram_id or not code:
        return TGRPCResponse(telegram_id=telegram_id or "", code=code or "", ok=False)

    try:
        async with Services.database.session() as session:
            await session.execute(
                update(User)
                .where(User.usercode == code)
                .values(tg_account=telegram_id)
            )
            await session.commit()
            return TGRPCResponse(telegram_id=str(telegram_id), code=str(code), ok=str(True))
    except Exception as e:
        LOGGER.exception(f"Account linking failed with error {e}")
        return TGRPCResponse(telegram_id=str(telegram_id), code=str(code), ok=str(False))

