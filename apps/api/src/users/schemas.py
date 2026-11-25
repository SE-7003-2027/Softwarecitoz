from pydantic import BaseModel


class User(BaseModel):
    id: int
    email: str | None = None
    steam_id: int | None = None
    status: str
    roles: list[str]