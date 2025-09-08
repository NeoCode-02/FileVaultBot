from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, BigInteger, DateTime, func, ForeignKey
from .database import Base
from typing import Optional


class Category(Base):
    __tablename__ = "categories"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    files: Mapped[list["File"]] = relationship(
        "File", back_populates="category", foreign_keys="File.category_id"
    )

    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}')>"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, unique=True, index=True
    )
    username: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    current_category_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("categories.id"), nullable=True
    )
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    files: Mapped[list["File"]] = relationship(
        "File", back_populates="user", cascade="all, delete-orphan"
    )

    current_category: Mapped[Optional["Category"]] = relationship(
        "Category", foreign_keys=[current_category_id]
    )

    def __repr__(self):
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, username=@{self.username})>"


class File(Base):
    __tablename__ = "files"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    unique_id: Mapped[str] = mapped_column(
        String(36), unique=True, nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    telegram_file_id: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), default="telegram_storage")

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id"), nullable=False
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user: Mapped["User"] = relationship("User", back_populates="files")

    category: Mapped["Category"] = relationship(
        "Category", back_populates="files", foreign_keys=[category_id]
    )

    def __repr__(self):
        return f"<File(id={self.id}, name='{self.name}', user_id={self.user_id})>"
