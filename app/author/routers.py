import os
import shutil
import uuid

from fastapi import Depends
from fastapi import File
from fastapi import HTTPException
from fastapi import status
from fastapi import UploadFile
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.auth.manager import create_access_jwt
from app.auth.manager import create_refresh_jwt
from app.auth.manager import verified_author
from app.author.schemas import PatchPassword
from app.author.schemas import PatchProfile
from app.author.schemas import Post
from app.config import project_dir
from app.config import settings
from app.db.conection import get_async_session
from app.db.models import Author


user_router = APIRouter(prefix="/api/author", tags=["author"])


@user_router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_post: Post, session: AsyncSession = Depends(get_async_session)):
    """
    Register a new user.

    Args:
        user_post: The user data
        session: The database session

    Returns:
        A dictionary with the user data and the access and refresh tokens
    """

    stmt = select(Author).where(Author.email == user_post.email)
    result = await session.execute(stmt)
    existing_user = result.scalars().first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already taken"
        )

    data = {"user_email": user_post.email}
    access_token = create_access_jwt(data)
    refresh_token = create_refresh_jwt(data)

    user_obj = Author(
        username=user_post.username,
        surname=user_post.surname,
        email=user_post.email,
        refresh_token=refresh_token,
    )

    user_obj.password = user_post.password

    session.add(user_obj)
    await session.commit()
    await session.refresh(user_obj)

    return {
        "user_id": user_obj.id,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "type": "bearer",
    }


@user_router.patch("/change_profile")
async def change_info(
    user_patch: PatchProfile,
    user: Author = Depends(verified_author),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Update the user profile

    Args:
        user_patch: The user data to be updated
        user: The authenticated user
        session: The database session

    Returns:
        A message indicating the profile was updated
    """
    user_data = user_patch.dict(exclude_unset=True)
    for key, value in user_data.items():
        if not value:
            continue
        setattr(user, key, value)

    await session.commit()
    return {"message": "Profile updated"}


@user_router.patch("/change_password")
async def change_password(
    author_patch: PatchPassword,
    author: Author = Depends(verified_author),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Change the user password

    Args:
        author_patch: The old and new password
        author: The authenticated user
        session: The database session

    Returns:
        A message indicating the password was updated
    """
    if not author.check_password(author_patch.old_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Wrong password"
        )

    author.password = author_patch.new_password
    await session.commit()
    return {"message": "Password updated"}


@user_router.get("/profile")
async def get_profile(author: Author = Depends(verified_author)):
    """
    get the user profile

    Args:
        author: The authenticated user

    Returns:
        The user profile
    """
    return author.get_all


@user_router.put("/profile/image")
async def update_user_image(
    image_file: UploadFile = File(...),
    session: AsyncSession = Depends(get_async_session),
    current_author: Author = Depends(verified_author),
):
    """
    update the user image file

    Args:
        image_file: The image file to be uploaded
        session: The database session
        current_author: The authenticated user

    Returns:
        A message indicating the image was updated
    """
    _, extension = os.path.splitext(image_file.filename)

    if extension not in [".jpg", ".jpeg", ".png", ".gif"]:
        raise HTTPException(status_code=400, detail="Invalid file type")

    filename = f"{uuid.uuid4()}{extension}"
    file_location = settings.STATIC_PATH / filename

    with file_location.open("wb") as buffer:
        shutil.copyfileobj(image_file.file, buffer)

    await image_file.close()

    if current_author.image != "static/no_image.png":
        image = project_dir.parent / current_author.image
        image.unlink()
    current_author.image = f"static/{filename}"
    session.add(current_author)
    await session.commit()

    return {"message": "Image updated"}


@user_router.delete("/profile/image")
async def delete_user_image(
    session: AsyncSession = Depends(get_async_session),
    current_author: Author = Depends(verified_author),
):
    """
    delete the user image file

    Args:
        session: The database session
        current_author: The authenticated user

    Returns:
        A message indicating the image was deleted
    """
    if current_author.image == "static/no_image.png":
        raise HTTPException(status_code=400, detail="No image to delete")
    image = project_dir.parent / current_author.image
    image.unlink()
    current_author.image = "static/no_image.png"
    session.add(current_author)
    await session.commit()

    return {"message": "Image deleted"}
