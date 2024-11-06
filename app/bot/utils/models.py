from pydantic import BaseModel


class UserData(BaseModel):
    id: int
    full_name: str
    score: int
    balance: int

