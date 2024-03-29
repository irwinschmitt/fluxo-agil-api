from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.models import Department


async def store_or_update_department(
    session: AsyncSession, sigaa_id: int, acronym: str, title: str
):
    """Store or update a department."""
    statement = select(Department).where(Department.sigaa_id == sigaa_id)
    result = await session.execute(statement)
    department = result.scalars().one_or_none()

    if department:
        department.acronym = acronym
        department.title = title
    else:
        department = Department(sigaa_id=sigaa_id, acronym=acronym, title=title)
        session.add(department)

    await session.commit()

    return department


async def get_department_by_acronym_and_title(
    session: AsyncSession, acronym: str, title: str
):
    """Get a department by its acronym and title."""

    expression = Department.acronym == acronym and Department.title == title

    result = await session.execute(select(Department).where(expression))

    return result.scalars().one()


async def get_department_by_title(session: AsyncSession, title: str):
    """Get a department by its title."""

    result = await session.execute(select(Department).where(Department.title == title))

    return result.scalars().one()
