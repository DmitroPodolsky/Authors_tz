from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import Table

from app.db.conection import Base

post_categories = Table(
    "post_categories",
    Base.metadata,
    Column(
        "post_id", Integer, ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True
    ),
    Column(
        "category_id",
        Integer,
        ForeignKey("categories.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)

post_tags = Table(
    "post_tags",
    Base.metadata,
    Column(
        "post_id", Integer, ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True
    ),
    Column(
        "tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True
    ),
)
