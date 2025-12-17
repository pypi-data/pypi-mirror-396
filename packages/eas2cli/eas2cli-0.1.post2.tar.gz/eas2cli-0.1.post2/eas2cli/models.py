from pydantic import BaseModel
from pydantic import Field
from typing import Optional
from typing import Literal


class Tokens(BaseModel):
    access_token: str
    refresh_token: Optional[str] = Field(default=None)
    scope: str = Field(default='fdsn')
    id_token: str
    token_type: Optional[Literal['Bearer']] = Field(default='Bearer')
    expires_in: Optional[int]
