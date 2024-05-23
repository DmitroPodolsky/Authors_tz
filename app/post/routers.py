from fastapi import Depends
from fastapi import HTTPException
from fastapi import Query
from fastapi import status
from fastapi.routing import APIRouter
from sqlalchemy import asc
from sqlalchemy import desc
from sqlalchemy import or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.auth.manager import verified_author
from app.db.conection import get_async_session
from app.db.models import Author
from app.db.models.category import Category
from app.db.models.post import Post
from app.db.models.tag import Tag
from app.post.schemas import PostCreate
from app.post.schemas import PostRetrieve
from app.post.services import convert_post_to_post_retrieve
from app.post.services import get_post


post_router = APIRouter(prefix="/api/post", tags=["posts"])


@post_router.post("/")
async def create_post(
    post_data: PostCreate,
    session: AsyncSession = Depends(get_async_session),
    current_author: Author = Depends(verified_author),
):
    """
    Create a new post if the authenticated author

    Args:
        post_data: The post data
        session: The database session
        current_author: The authenticated author

    Returns:
        The created post
    """
    categories = await session.execute(
        select(Category).filter(Category.name.in_(post_data.category_names))
    )
    categories = categories.scalars().all()
    if len(categories) != len(post_data.category_names):
        existing_category_names = [category.name for category in categories]
        missing_categories = set(post_data.category_names) - set(
            existing_category_names
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Categories not found: {', '.join(missing_categories)}",
        )

    tags = []
    for tag_name in post_data.tag_names:
        tag = await session.execute(select(Tag).filter(Tag.name == tag_name))
        tag = tag.scalars().first()
        if not tag:
            tag = Tag(name=tag_name)
        tags.append(tag)

    post = Post(
        title=post_data.title,
        description=post_data.description,
        author_id=current_author.id,
        categories=categories,
        tags=tags,
    )
    session.add(post)

    await session.commit()
    await session.refresh(post)
    return convert_post_to_post_retrieve(post)


@post_router.patch("/posts/{post_id}")
async def update_post(
    post_id: int,
    title: str = None,
    description: str = None,
    category_names: list[str] = None,
    tag_names: list[str] = None,
    session: AsyncSession = Depends(get_async_session),
    current_author: Author = Depends(verified_author),
):
    """
    Update a post by its id if the authenticated author is the author of the post

    Args:
        post_id: The id of the post to be updated
        title: The new title of the post
        description: The new description of the post
        category_names: The new category names of the post
        tag_names: The new tag names of the post
        session: The database session
        current_author: The authenticated author

    Returns:
        The updated post
    """
    post = await get_post(post_id, session)
    if not post or post.author_id != current_author.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found or you are not the author of this post",
        )

    if title:
        post.title = title
    if description:
        post.description = description

    categories = []
    tags = []

    if category_names:
        result = await session.execute(
            select(Category).filter(Category.name.in_(category_names))
        )
        categories = result.scalars().all()
        if len(categories) != len(category_names):
            existing_category_names = [category.name for category in categories]
            missing_categories = set(category_names) - set(existing_category_names)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Categories not found: {', '.join(missing_categories)}",
            )
        post.categories = categories

    if tag_names:
        tags = []
        for tag_name in tag_names:
            result = await session.execute(select(Tag).filter(Tag.name == tag_name))
            tag = result.scalars().first()
            if not tag:
                tag = Tag(name=tag_name)
            tags.append(tag)
        post.tags = tags

    session.add(post)
    await session.commit()
    await session.refresh(post)
    return convert_post_to_post_retrieve(post)


@post_router.get("/posts/{post_id}", response_model=PostRetrieve)
async def get_single_post(
    post_id: int, session: AsyncSession = Depends(get_async_session)
):
    """
    Get a single post by its id

    Args:
        post_id: The id of the post to be retrieved
        session: The database session

    Returns:
        The post with the given id
    """

    result = await session.execute(
        select(Post)
        .filter(Post.id == post_id)
        .options(selectinload(Post.categories), selectinload(Post.tags))
    )
    post = result.scalars().first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    return convert_post_to_post_retrieve(post)


@post_router.get("/posts", response_model=list[PostRetrieve])
async def get_all_posts(session: AsyncSession = Depends(get_async_session)):
    """
    Get all posts

    Args:
        session: The database session

    Returns:
        A list of all posts
    """
    result = await session.execute(
        select(Post).options(selectinload(Post.categories), selectinload(Post.tags))
    )
    posts = result.scalars().all()
    return [convert_post_to_post_retrieve(post) for post in posts]


@post_router.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_author: Author = Depends(verified_author),
):
    """
    Delete a post by its id if the authenticated author is the author of the post

    Args:
        post_id: The id of the post to be deleted
        session: The database session
        current_author: The authenticated author

    Returns:
        A message indicating the post was deleted successfully
    """
    post = await session.execute(select(Post).filter(Post.id == post_id))
    post = post.scalars().first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    if post.author_id != current_author.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not the author of this post",
        )

    await session.delete(post)
    await session.commit()

    return {"message": "Post deleted successfully"}


@post_router.get("/posts/search/")
async def search_posts(
    category_names: list[str] = Query(None),
    tag_names: list[str] = Query(None),
    order_by: str = Query("desc"),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Search posts by categories and tags and order by updated_at

    Args:
        category_names: list of category names
        tag_names: list of tag names
        order_by: order by updated_at field. Default is 'desc'
        session: The database session

    Returns:
        A list of posts that match the search criteria
    """
    existing_categories = []
    existing_tags = []

    if category_names:
        existing_categories = await session.execute(
            select(Category).filter(Category.name.in_(category_names))
        )
        existing_categories = [
            category.name for category in existing_categories.scalars()
        ]
        not_found_categories = set(category_names) - set(existing_categories)
        if not_found_categories:
            raise HTTPException(
                status_code=404,
                detail=f"Not found categories: {', '.join(not_found_categories)}",
            )

    if tag_names:
        existing_tags = await session.execute(
            select(Tag).filter(Tag.name.in_(tag_names))
        )
        existing_tags = [tag.name for tag in existing_tags.scalars()]
        not_found_tags = set(tag_names) - set(existing_tags)
        if not_found_tags:
            raise HTTPException(
                status_code=404,
                detail=f"Next tags not found: {', '.join(not_found_tags)}",
            )

    query = select(Post)

    if existing_categories:
        query = query.filter(
            or_(
                Post.categories.any(Category.name == category_name)
                for category_name in existing_categories
            )
        )
    if existing_tags:
        query = query.filter(
            or_(Post.tags.any(Tag.name == tag_name) for tag_name in existing_tags)
        )

    if order_by == "desc":
        query = query.order_by(desc(Post.updated_at))
    elif order_by == "asc":
        query = query.order_by(asc(Post.updated_at))
    else:
        raise HTTPException(
            status_code=400,
            detail="Does not support this order_by value. Use 'desc' or 'asc'",
        )

    posts = await session.execute(query)
    return posts.scalars().all()
