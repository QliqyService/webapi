from uuid import UUID

from pydantic import BaseModel


class QRRPCRequest(BaseModel):
    id: UUID
    url: str


class QRRPCResponse(BaseModel):
    id: UUID
    body: str
