from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.manager import verified_author
from app.category.schemas import CategoryRetrieve
from app.db.conection import get_async_session
from app.db.models.author import Author
from app.db.models.category import Category

category_router = APIRouter(prefix="/api/category", tags=["categories"])


@category_router.post("/categories/", response_model=CategoryRetrieve)
async def create_category(
    name: str,
    session: AsyncSession = Depends(get_async_session),
    current_author: Author = Depends(verified_author),
):
    """
    create a new category if authenticated author

    Args:
        name: The name of the category
        session: The database session
        current_author: The authenticated author

    Returns:
        The created category
    """
    existing_category = await session.execute(
        select(Category).filter(Category.name == name)
    )
    existing_category = existing_category.scalar()

    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Category already exists"
        )

    new_category = Category(name=name)
    session.add(new_category)
    await session.commit()

    return new_category


@category_router.get("/categories/", response_model=list[CategoryRetrieve])
async def get_categories(session: AsyncSession = Depends(get_async_session)):
    """
    get all categories

    Args:
        session: The database session

    Returns:
        A list of all categories
    """
    result = await session.execute(select(Category))
    return result.scalars().all()


@category_router.get("/categories/{category_id}", response_model=CategoryRetrieve)
async def get_category(
    category_id: int, session: AsyncSession = Depends(get_async_session)
):
    """
    get a category by its id

    Args:
        category_id: The id of the category to be retrieved
        session: The database session

    Returns:
        The category with the given id
    """
    category = await session.get(Category, category_id)
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )
    return category


@category_router.put("/categories/{category_id}", response_model=CategoryRetrieve)
async def update_category(
    category_id: int,
    name: str,
    session: AsyncSession = Depends(get_async_session),
    current_author: Author = Depends(verified_author),
):
    """
    Update a category by its id if authenticated author is the creator of the category.

    Args:
        category_id: The id of the category to be updated
        name: The new name of the category
        session: The database session
        current_author: The authenticated author

    Returns:
        A message indicating the category has been updated
    """
    category = await session.get(Category, category_id)
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )

    category.name = name

    await session.commit()
    return {"message": "Category updated"}


@category_router.delete(
    "/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_category(
    category_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_author: Author = Depends(verified_author),
):
    """
    Delete a category by its id if authenticated author is the creator of the category.

    Args:
        category_id: The id of the category to be deleted
        session: The database session
        current_author: The authenticated author

    Returns:
        A message indicating the category has been deleted
    """
    category = await session.get(Category, category_id)
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )

    await session.delete(category)
    await session.commit()

    return {"message": "Category deleted"}
