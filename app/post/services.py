from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.conection import get_async_session
from app.db.models.post import Post
from app.post.schemas import CategorySchema
from app.post.schemas import PostRetrieve
from app.post.schemas import TagSchema


async def get_post(post_id: int, session: AsyncSession):
    """
    Get a post by its id.

    Args:
        post_id: The id of the post
        session: The database session

    Returns:
        The post
    """
    result = await session.execute(select(Post).filter_by(id=post_id))
    post = result.scalars().first()
    return post


def convert_post_to_post_retrieve(post: Post) -> PostRetrieve:
    """
    Convert a Post object to a PostRetrieve object.

    Args:
        post: The Post object

    Returns:
        The PostRetrieve object
    """
    categories = [CategorySchema(name=category.name) for category in post.categories]
    tags = [TagSchema(name=tag.name) for tag in post.tags]
    return PostRetrieve(
        id=post.id,
        title=post.title,
        description=post.description,
        user_id=post.author_id,
        created_at=post.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        updated_at=post.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
        categories=categories,
        tags=tags,
    )
