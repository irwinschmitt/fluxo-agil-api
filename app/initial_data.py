"""
Put here any Python code that must be runned before application startup.
It is included in `init.sh` script.

By defualt `main` create a superuser if not exists
"""

import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import config, security
from app.core.session import async_session
from app.models import Department, User


async def create_superuser(session: AsyncSession):
    result = await session.execute(
        select(User).where(User.email == config.settings.FIRST_SUPERUSER_EMAIL)
    )

    user = result.scalars().first()

    if user is None:
        new_superuser = User(
            email=config.settings.FIRST_SUPERUSER_EMAIL,
            hashed_password=security.get_password_hash(
                config.settings.FIRST_SUPERUSER_PASSWORD
            ),
        )
        session.add(new_superuser)
        await session.commit()

        print("Superuser was created")
    else:
        print("Superuser already exists in database")


async def create_departments(session: AsyncSession):
    departments = await session.execute(select(Department))

    if departments.scalar() is None:
        new_department = Department(
            sigaa_id=673, acronym="FGA", title="Faculdade do Gama"
        )

        session.add(new_department)
        await session.commit()
        await session.refresh(new_department)

        print('"', new_department.title, '" department was created', sep="")

    else:
        print("Departments already exists")


async def main() -> None:
    async with async_session() as session:
        await create_superuser(session)
        await create_departments(session)

        print("Initial data created")


if __name__ == "__main__":
    asyncio.run(main())
