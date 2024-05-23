from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import relationship

from app.db.conection import Base
from app.db.models import post_categories
from app.db.models import post_tags


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True)
    title = Column(String(50))
    description = Column(String(1000))
    author_id = Column(Integer, ForeignKey("authors.id", ondelete="CASCADE"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow, default=datetime.utcnow)

    author = relationship("Author", back_populates="posts")
    categories = relationship(
        "Category", secondary=post_categories, back_populates="posts", lazy="subquery"
    )
    tags = relationship(
        "Tag", secondary=post_tags, back_populates="posts", lazy="subquery"
    )
