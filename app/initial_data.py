import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import config, security
from app.core.session import async_session
from app.db.models import User
from app.scraper.main import create_sigaa_data


async def create_superuser(session: AsyncSession):
    print("Creating superuser...")

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

        print("Superuser created")
    else:
        print("Superuser already exists")


async def main() -> None:
    async with async_session() as session:
        await create_superuser(session)
        await create_sigaa_data(session)


if __name__ == "__main__":
    asyncio.run(main())
