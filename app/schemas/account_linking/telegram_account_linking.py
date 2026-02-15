from pydantic import BaseModel


class TGRPCRequest(BaseModel):
    code: str
    telegram_id: str


class TGRPCResponse(BaseModel):
    code: str
    telegram_id: str
    ok: str
