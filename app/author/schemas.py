from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import Field


class Post(BaseModel):
    email: EmailStr
    username: str = Field(max_length=50)
    surname: str = Field(max_length=50)
    password: str = Field(min_length=8, max_length=20)


class PatchProfile(BaseModel):
    username: str | None = Field(max_length=50, default=None)
    surname: str | None = Field(max_length=50, default=None)
    email: EmailStr | None


class PatchPassword(BaseModel):
    old_password: str
    new_password: str = Field(min_length=8, max_length=20)
