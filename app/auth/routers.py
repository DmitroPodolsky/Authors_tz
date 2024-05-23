from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.auth.manager import create_access_jwt
from app.auth.manager import create_refresh_jwt
from app.auth.manager import get_token_data
from app.auth.manager import refresh_token
from app.auth.manager import verified_author
from app.auth.schemas import UserLogin
from app.db.conection import get_async_session
from app.db.models import Author

auth_router = APIRouter(prefix="/api/auth", tags=["auth"])


@auth_router.post("/login")
async def login(body: UserLogin, session: AsyncSession = Depends(get_async_session)):
    """
    Login the user with the given credentials.

    Args:
        body: The user credentials
        session: The database session

    Returns:
        A dictionary with the user data and the access and refresh tokens
    """

    error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="wrong credentials",
    )

    stmt = select(Author).where(Author.email == body.email)
    result = await session.execute(stmt)
    user = result.scalars().first()

    if not user:
        raise error

    if not user.check_password(body.password):
        raise error

    data = {"user_email": user.email}
    access_token = create_access_jwt(data)
    refresh_token = create_refresh_jwt(data)

    user.refresh_token = refresh_token
    await session.commit()

    return {
        "message": "Login Successful",
        "username": user.username,
        "surname": user.surname,
        "email": user.email,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "type": "bearer",
    }


@auth_router.post("/refresh_token")
async def refresh(token_data: dict = Depends(refresh_token)):
    """
    refresh the token

    Args:
        token_data: The token data

    Returns:
        The token data
    """
    return token_data


@auth_router.post("/logout")
async def logout(
    data: str = Depends(get_token_data),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Logout user by invalidating the refresh token.

    Args:
        token: The refresh token provided by the user.
        session: The database session.

    Returns:
        A message indicating the user has been logged out.
    """
    stmt = select(Author).where(Author.email == data["user_email"])
    result = await session.execute(stmt)
    user = result.scalars().first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    user.refresh_token = None
    await session.commit()

    return {"message": "Successfully logged out"}
