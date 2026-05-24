from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class UserCreate(BaseModel):
    username: str
    password: str
    role: str
    linked_entity_id: Optional[int] = None

class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    linked_entity_id: Optional[int] = None

    class Config:
        from_attributes = True
