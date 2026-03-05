from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship, Session

from .database import Base, get_session


class Post(Base):
    __tablename__ = "posts"

    id: int = Column(Integer, primary_key=True, index=True)
    title: str = Column(String(255), nullable=False, index=True)
    content: str = Column(Text, nullable=False)
    created_at: datetime = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: datetime = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    user_id: int = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    author = relationship("User", back_populates="posts")

    @classmethod
    def create(cls, *, title: str, content: str, user_id: int) -> "Post":
        session: Session = get_session()
        new_post = cls(title=title, content=content, user_id=user_id)
        session.add(new_post)
        session.commit()
        session.refresh(new_post)
        return new_post

    @classmethod
    def read(cls, *, post_id: int) -> Optional["Post"]:
        session: Session = get_session()
        return session.query(cls).filter_by(id=post_id).first()

    @classmethod
    def list_by_user(cls, *, user_id: int, skip: int = 0, limit: int = 100) -> list["Post"]:
        session: Session = get_session()
        return (
            session.query(cls)
            .filter_by(user_id=user_id)
            .order_by(cls.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update(self, *, title: Optional[str] = None, content: Optional[str] = None) -> "Post":
        session: Session = get_session()
        if title is not None:
            self.title = title
        if content is not None:
            self.content = content
        session.add(self)
        session.commit()
        session.refresh(self)
        return self

    def delete(self) -> None:
        session: Session = get_session()
        session.delete(self)
        session.commit()

    @property
    def summary(self) -> str:
        return (self.content[:97] + "...") if len(self.content) > 100 else self.content

    @staticmethod
    def validate_title(value: str) -> str:
        if not value or not isinstance(value, str):
            raise ValueError("Title must be a non-empty string")
        if len(value) > 255:
            raise ValueError("Title exceeds maximum length of 255 characters")
        return value

    @staticmethod
    def validate_content(value: str) -> str:
        if not value or not isinstance(value, str):
            raise ValueError("Content must be a non-empty string")
        return value

    def __repr__(self) -> str:
        return f"<Post id={self.id} title='{self.title[:20]}' user_id={self.user_id}>"