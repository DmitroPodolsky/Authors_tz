from pydantic import BaseModel


class PostCreate(BaseModel):
    title: str
    description: str
    category_names: list[str]
    tag_names: list[str]


class CategorySchema(BaseModel):
    name: str


class TagSchema(BaseModel):
    name: str


class PostRetrieve(BaseModel):
    id: int
    title: str
    description: str
    user_id: int
    created_at: str
    updated_at: str
    categories: list[CategorySchema]
    tags: list[TagSchema]
