from datetime import datetime

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import relationship
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

from app.db.conection import Base


class Author(Base):
    __tablename__ = "authors"

    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    surname = Column(String(50))
    email = Column(String(120), unique=True)
    password_hash = Column("password", String(256), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    isadmin = Column(Boolean, default=False, nullable=False)
    refresh_token = Column(String(1000), nullable=True)

    image = Column(String(1000), default="static/no_image.png")

    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")

    @property
    def password(self):
        raise AttributeError("password: write-only field")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
