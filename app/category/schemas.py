from pydantic import BaseModel


class CategoryRetrieve(BaseModel):
    id: int
    name: str
