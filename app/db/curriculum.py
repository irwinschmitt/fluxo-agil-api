from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.models import Curriculum


async def store_or_update_curriculum(session: AsyncSession, curriculum: Curriculum):
    """Store or update a curriculum."""

    expression = Curriculum.sigaa_id == curriculum.sigaa_id
    result = await session.execute(select(Curriculum).where(expression))
    current_curriculum = result.scalars().one_or_none()

    if current_curriculum:
        current_curriculum = curriculum

    else:
        session.add(curriculum)

    await session.commit()

    return current_curriculum
