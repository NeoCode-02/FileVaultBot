from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import File, Category
import uuid


async def get_general_category(session: AsyncSession) -> Category:
    """Get or create the General category"""
    result = await session.execute(select(Category).where(Category.name == "General"))
    category = result.scalar_one_or_none()

    if not category:
        category = Category(name="General")
        session.add(category)
        await session.commit()

    return category


async def create_file_record(
    session: AsyncSession, file_data: dict, user_id: int, category_id: int
) -> File:
    """Create a new file record in database with category"""
    new_file = File(
        unique_id=str(uuid.uuid4())[:8],
        **file_data,
        user_id=user_id,
        category_id=category_id,
    )
    session.add(new_file)
    await session.commit()
    await session.refresh(new_file)
    return new_file


async def get_user_files(
    session: AsyncSession, user_id: int, offset: int = 0, limit: int = 10
):
    """Get user's files with pagination"""
    from sqlalchemy import select
    from app.models import File

    result = await session.execute(
        select(File)
        .where(File.user_id == user_id)
        .order_by(File.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    return result.scalars().all()


async def get_user_files_count(session: AsyncSession, user_id: int) -> int:
    """Get total number of files for a user"""
    from sqlalchemy import select, func
    from app.models import File

    result = await session.execute(
        select(func.count(File.id)).where(File.user_id == user_id)
    )
    return result.scalar() or 0
