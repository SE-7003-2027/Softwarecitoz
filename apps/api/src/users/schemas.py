from pydantic import BaseModel


class User(BaseModel):
    id: int
    status: str
    roles: list[str]
