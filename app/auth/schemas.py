from pydantic import BaseModel
from pydantic import EmailStr


class UserLogin(BaseModel):
    email: EmailStr
    password: str
