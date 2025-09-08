from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import Optional
from app.models import Category, User


async def get_user_categories(session: AsyncSession, user_id: int) -> list[Category]:
    """Get all categories that have files belonging to a user"""
    result = await session.execute(
        select(Category)
        .join(Category.files)
        .where(Category.files.any(user_id=user_id))
        .distinct()
        .order_by(Category.name)
    )
    return result.scalars().all()


async def get_or_create_category(
    session: AsyncSession, category_name: str, user_id: int
) -> Category:
    """Get existing category or create a new one for the user"""
    result = await session.execute(
        select(Category).where(Category.name.ilike(category_name))
    )
    category = result.scalar_one_or_none()

    if not category:
        category = Category(name=category_name)
        session.add(category)
        await session.commit()
        await session.refresh(category)

    return category


async def set_user_current_category(
    session: AsyncSession, user_id: int, category_id: Optional[int]
):
    """Set user's current category for uploads"""
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one()
    user.current_category_id = category_id
    await session.commit()


async def get_user_current_category(
    session: AsyncSession, user_id: int
) -> Optional[Category]:
    """Get user's current category - create General if not exists"""
    from app.services.file_service import get_general_category

    result = await session.execute(
        select(User)
        .where(User.id == user_id)
        .options(selectinload(User.current_category))
    )
    user = result.scalar_one()

    if not user.current_category:
        general_category = await get_general_category(session)
        user.current_category_id = general_category.id
        await session.commit()
        await session.refresh(user)
        return general_category

    return user.current_category


async def ensure_user_has_category(session: AsyncSession, user_id: int) -> Category:
    """Ensure user has a current category set"""
    current_category = await get_user_current_category(session, user_id)
    if not current_category:
        from app.services.file_service import get_general_category

        current_category = await get_general_category(session)
        await set_user_current_category(session, user_id, current_category.id)
    return current_category
