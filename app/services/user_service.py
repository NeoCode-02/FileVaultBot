from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import User
from sqlalchemy.orm import selectinload

async def get_or_create_user(session: AsyncSession, telegram_user) -> User:
    """Get user from DB or create if not exists"""
    result = await session.execute(
        select(User)
        .where(User.telegram_id == telegram_user.id)
        .options(selectinload(User.files))
    )
    db_user = result.scalar_one_or_none()

    if db_user is None:
        db_user = User(
            telegram_id=telegram_user.id,
            username=telegram_user.username,
            first_name=telegram_user.first_name,
            last_name=telegram_user.last_name,
        )
        session.add(db_user)
        await session.commit()
        await session.refresh(db_user)
        result = await session.execute(
            select(User)
            .where(User.telegram_id == telegram_user.id)
            .options(selectinload(User.files))
        )
        db_user = result.scalar_one_or_none()

    return db_user
