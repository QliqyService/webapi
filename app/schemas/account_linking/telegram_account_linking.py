from pydantic import BaseModel


class TGRPCRequest(BaseModel):
    code: str
    telegram_id: str
    telegram_username: str | None = None


class TGRPCResponse(BaseModel):
    code: str
    telegram_id: str
    ok: str
