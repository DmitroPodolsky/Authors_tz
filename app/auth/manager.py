from datetime import datetime

from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from fastapi.security import HTTPBearer
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from jose.exceptions import JWTError
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.config import settings
from app.db.conection import get_async_session
from app.db.models import Author

security = HTTPBearer()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth_scheme = OAuth2PasswordBearer(tokenUrl="/token")

ERROR = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid authorization credentials"
)


def create_access_jwt(data: dict[str, str]) -> str:
    """
    Create an access token with the given data.

    Args:
        data: The data to be encoded in the token

    Returns:
        The encoded token
    """

    data["exp"] = datetime.utcnow() + settings.JWT_ACCESS_EXP
    data["mode"] = "access_token"
    return jwt.encode(data, settings.SECRET, settings.ALGORITHM)


def create_refresh_jwt(data: dict[str, str]) -> str:
    """
    Create a refresh token with the given data.

    Args:
        data: The data to be encoded in the token

    Returns:
        The encoded token
    """

    data["exp"] = datetime.utcnow() + settings.JWT_REFRESH_EXP
    data["mode"] = "refresh_token"
    return jwt.encode(data, settings.SECRET, settings.ALGORITHM)


async def get_token_data(token: str = Depends(oauth_scheme)) -> dict[str, str]:
    """
    Get the data from the given token.

    Args:
        token: The token to be decoded

    Returns:
        The decoded token data
    """

    try:
        data = jwt.decode(token, settings.SECRET, settings.ALGORITHM)
        data["token"] = token
    except JWTError:
        raise ERROR

    if "user_email" not in data and "mode" not in data:
        raise ERROR

    return data


async def refresh_token(
    data: str = Depends(get_token_data),
    session: AsyncSession = Depends(get_async_session),
) -> dict[str, str]:
    """
    Refresh the given token.

    Args:
        token: The token to be refreshed
        session: The database session

    Returns:
        A dictionary with the new access,refresh tokens and the token type
    """

    if data["mode"] != "refresh_token":
        raise ERROR

    stmt = select(Author).where(Author.email == data["user_email"])
    result = await session.execute(stmt)
    author = result.scalars().first()

    if not author or data["token"] != author.refresh_token:
        raise ERROR

    refresh_tkn = create_refresh_jwt(data)
    author.refresh_token = refresh_tkn
    await session.commit()

    # generate new access token
    access_tkn = create_access_jwt(data)
    return {"access_token": access_tkn, "refresh_token": refresh_tkn, "type": "bearer"}


async def verified_author(
    data: str = Depends(get_token_data),
    session: AsyncSession = Depends(get_async_session),
    authorization: str = Depends(security),
) -> Author:
    """
    Verify the given token and return the user.

    Args:
        token: The token to be verified
        session: The database session

    Returns:
        The user associated with the token
    """

    if data["mode"] != "access_token":
        raise ERROR

    stmt = select(Author).where(Author.email == data["user_email"])
    result = await session.execute(stmt)
    author = result.scalars().first()

    if not author:
        raise ERROR

    if not author.refresh_token:
        raise ERROR

    return author
