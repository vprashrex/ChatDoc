from pydantic import BaseModel


class User(BaseModel):
    email: str
    password: str

class UserInDB(BaseModel):
    email: str
    hashed_password: str
    user_id: str


class TokenData(BaseModel):
    email: str = None

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

    