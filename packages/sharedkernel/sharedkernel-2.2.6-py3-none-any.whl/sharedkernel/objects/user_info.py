from pydantic import BaseModel   

from contextvars import ContextVar

class UserInfo(BaseModel):
    nameid: str
    role: str | None = None
    org_token: str | None = None
    org_user_id: str | None = None

current_user_info: ContextVar[UserInfo] = ContextVar("current_user_info")

