import asyncio

from pyppeteer import launch
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.session import async_session
from app.scraper.courses import get_programs
from app.scraper.departments import create_departments, get_departments


async def create_sigaa_data(session: AsyncSession):
    browser = await launch(headless=True, executablePath="/usr/bin/google-chrome")

    departments = await get_departments(browser)
    await create_departments(session, departments)

    programs = await get_programs(browser, session)
    print(f"[TODO] Create {len(programs)} programs")

    await browser.close()


async def main():
    async with async_session() as session:
        await create_sigaa_data(session)


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
