from datetime import datetime
from enum import Enum
from enum import unique

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.config import settings
from app.db.conection import Base
from app.db.models import post_categories


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)

    posts = relationship("Post", secondary=post_categories, back_populates="categories")
