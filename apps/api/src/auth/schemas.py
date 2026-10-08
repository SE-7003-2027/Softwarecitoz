from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class SessionOut(BaseModel):
    id: UUID
    created_at: datetime
    last_used_at: datetime
    user_agent: str | None
