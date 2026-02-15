from pydantic import BaseModel, Field


class GetHealthcheckResponse(BaseModel):
    msg: str = Field(default="OK")
    release: str = Field(default="not-set")
