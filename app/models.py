from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, BigInteger, DateTime, func, ForeignKey, Text
from .database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, unique=True, index=True
    )
    username: Mapped[None | str] = mapped_column(String(100), nullable=True)
    first_name: Mapped[None | str] = mapped_column(String(100), nullable=True)
    last_name: Mapped[None | str] = mapped_column(String(100), nullable=True)
    phone: Mapped[None | str] = mapped_column(String(100), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    files: Mapped[list["File"]] = relationship(
        "File", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, username=@{self.username})>"


class Category(Base):
    __tablename__ = "categories"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    files: Mapped[list["File"]] = relationship("File", back_populates="category")

    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}')>"


class File(Base):
    __tablename__ = "files"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id"), nullable=False
    )
    file_path: Mapped[str] = mapped_column(String(500), nullable=False, unique=True)
    unique_id: Mapped[str] = mapped_column(
        String(36), unique=True, nullable=False, index=True
    )
    mime_type: Mapped[None | str] = mapped_column(String(100), nullable=True)
    size: Mapped[None | int] = mapped_column(Integer, nullable=True)
    caption: Mapped[None | str] = mapped_column(Text, nullable=True)
    telegram_file_id: Mapped[None | str] = mapped_column(String(255), nullable=True)

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user: Mapped["User"] = relationship("User", back_populates="files")
    category: Mapped["Category"] = relationship("Category", back_populates="files")

    def __repr__(self):
        return f"<File(id={self.id}, name='{self.name}', user_id={self.user_id})>"
