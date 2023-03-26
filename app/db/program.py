from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.models import Program


async def store_or_update_program(session: AsyncSession, program: Program):
    """Store or update a program."""

    expression = Program.sigaa_id == program.sigaa_id
    result = await session.execute(select(Program).where(expression))
    current_program = result.scalars().one_or_none()

    if current_program:
        current_program = program

    else:
        session.add(program)

    await session.commit()

    return current_program
