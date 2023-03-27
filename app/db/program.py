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


async def get_programs(session: AsyncSession):
    """Get all programs."""

    result = await session.execute(select(Program))
    programs = result.scalars().all()

    return programs


async def get_program_by_sigaa_id(session: AsyncSession, sigaa_id: int):
    """Get a program by its SIGAA ID."""

    expression = Program.sigaa_id == sigaa_id
    result = await session.execute(select(Program).where(expression))
    program = result.scalars().one_or_none()

    return program
